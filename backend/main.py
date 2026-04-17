from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import torch
import torch.nn as nn
import joblib
import os
import io
import json
import numpy as np
import pandas as pd
from PIL import Image
from torchvision import transforms
from datetime import datetime
from models import RecyclingClassifier, RecycleTrendRNN

app = FastAPI()

# CORS
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])
app.mount("/static", StaticFiles(directory="static"), name="static")

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
if torch.backends.mps.is_available(): device = torch.device("mps")

# Inventory Persistence
INVENTORY_FILE = "models/inventory.json"
if not os.path.exists(INVENTORY_FILE):
    with open(INVENTORY_FILE, 'w') as f:
        json.dump([], f)

# Yoğunluk Tablosu
DENSITY_TABLE = {
    'glass': 650, 'metal': 450, 'plastic': 95,
    'paper': 150, 'cardboard': 75, 'trash': 300
}

# Lazy Load Models
MODELS = {}

def load_models():
    if not MODELS:
        classes = joblib.load('models/classes.pkl')
        # CNN
        model = RecyclingClassifier(len(classes)).to(device)
        model.load_state_dict(torch.load('models/recycle_model.pth', map_location=device))
        model.eval()
        # KNN
        knn = joblib.load('models/knn_similarity.pkl')
        feats_db = joblib.load('models/features_db.pkl')
        labels_db = joblib.load('models/labels_db.pkl')
        # RNN
        rnn = RecycleTrendRNN().to(device)
        if os.path.exists('models/rnn_trend_model.pth'):
            rnn.load_state_dict(torch.load('models/rnn_trend_model.pth', map_location=device))
        rnn.eval()
        
        MODELS.update({
            'model': model, 
            'classes': classes, 
            'knn': knn, 
            'feats_db': feats_db,
            'labels_db': labels_db,
            'rnn': rnn
        })
    return MODELS

# Transform
transform = transforms.Compose([
    transforms.Resize((224, 224)),
    transforms.ToTensor(),
    transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])
])

def calculate_impact(waste_type, weight_g, distance_km=0.0):
    weight_kg = weight_g / 1000.0
    impacts = {
        'paper': {'trees': 0.017, 'water': 26, 'energy': 4000, 'co2_credit': 0.5},
        'cardboard': {'trees': 0.017, 'water': 26, 'energy': 4000, 'co2_credit': 0.5},
        'glass': {'trees': 0, 'water': 0.2, 'energy': 300, 'co2_credit': 0.3},
        'plastic': {'trees': 0, 'water': 0.1, 'energy': 6000, 'co2_credit': 1.5},
        'metal': {'trees': 0, 'water': 0.5, 'energy': 14000, 'co2_credit': 2.0},
        'trash': {'trees': -0.001, 'water': -1.0, 'energy': -500, 'co2_credit': -0.5}
    }
    factors = impacts.get(waste_type.lower(), impacts['trash'])
    transport_co2 = (distance_km * 0.1)
    net_co2 = (weight_kg * factors['co2_credit']) - transport_co2
    return {
        'trees_saved': round(weight_kg * factors['trees'], 4),
        'water_saved': round(weight_kg * factors['water'], 2),
        'energy_saved': round(weight_kg * factors['energy'], 1),
        'net_co2': round(net_co2, 3)
    }

@app.post("/predict")
async def predict(file: UploadFile = File(...), distance: float = Form(5.0), volume: float = Form(1.0)):
    try:
        models = load_models()
        contents = await file.read()
        image = Image.open(io.BytesIO(contents)).convert('RGB')
        img_tensor = transform(image).unsqueeze(0).to(device)
        
        with torch.no_grad():
            # CNN Prediction
            logits = models['model'](img_tensor)
            prob = torch.softmax(logits, dim=1)
            conf, pred_idx = torch.max(prob, 1)
            waste_type = models['classes'][pred_idx.item()].lower()
            
            # KNN Similarity
            feats = models['model'](img_tensor, return_features=True)
            dist, indices = models['knn'].kneighbors(feats.cpu().numpy())
            # Benzer öğelerin sınıflarını al
            similar_items = [models['classes'][models['labels_db'][idx]] for idx in indices[0]]

        weight = volume * DENSITY_TABLE.get(waste_type, 300)
        impact = calculate_impact(waste_type, weight, distance)
        
        return {
            "waste_type": waste_type.capitalize(),
            "calculated_weight_g": round(weight, 1),
            "confidence": round(conf.item(), 4),
            "impact": impact,
            "similar_items": similar_items[:3],
            "is_recyclable": pred_idx.item() < 5,
            "cm_url": "http://localhost:8000/static/confusion_matrix.png",
            "roc_url": "http://localhost:8000/static/roc_curve.png",
            "metrics_url": "http://localhost:8000/static/metrics_score.png"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/history")
async def get_history():
    try:
        models = load_models()
        # 1. Yıllık Geçmişi Oku
        df = pd.read_csv('models/history.csv')
        history_points = df.tail(100).to_dict('records') # Son 100 gün tablo için
        
        # 2. RNN Tahmini (Gelecek 7 günün toplamı)
        last_7_days = df['weight_kg'].values[-7:]
        x_input = torch.tensor(last_7_days).float().view(1, 7, 1).to(device)
        
        with torch.no_grad():
            forecast_raw = models['rnn'](x_input).item()
        
        # 3. Envanteri Oku
        with open(INVENTORY_FILE, 'r') as f:
            inventory = json.load(f)

        return {
            "daily_history": history_points,
            "next_month_forecast_kg": round(forecast_raw * 30, 2), # Basit projeksiyon
            "inventory": inventory
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/add-to-inventory")
async def add_to_inventory(item: dict):
    with open(INVENTORY_FILE, 'r') as f:
        inventory = json.load(f)
    item['date'] = datetime.now().strftime("%Y-%m-%d %H:%M")
    inventory.append(item)
    with open(INVENTORY_FILE, 'w') as f:
        json.dump(inventory[-20:], f) 
    return {"status": "success"}

@app.post("/deliver-inventory")
async def deliver_inventory():
    try:
        with open(INVENTORY_FILE, 'r') as f:
            inventory = json.load(f)
        if not inventory: raise HTTPException(status_code=400, detail="Envanter boş!")
        total_weight_kg = sum([item['weight'] for item in inventory]) / 1000.0
        df = pd.read_csv('models/history.csv')
        today_str = datetime.now().strftime("%Y-%m-%d")
        if today_str in df['date'].values:
            df.loc[df['date'] == today_str, 'weight_kg'] += total_weight_kg
        else:
            new_row = pd.DataFrame([{'date': today_str, 'weight_kg': total_weight_kg}])
            df = pd.concat([df, new_row], ignore_index=True)
        df.to_csv('models/history.csv', index=False)
        with open(INVENTORY_FILE, 'w') as f: json.dump([], f)
        return {"status": "success", "delivered_weight_kg": round(total_weight_kg, 2)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/history/edit")
async def edit_history(data: dict):
    try:
        df = pd.read_csv('models/history.csv')
        date = data['date']; new_weight = data['weight_kg']
        if date in df['date'].values:
            df.loc[df['date'] == date, 'weight_kg'] = new_weight
            df.to_csv('models/history.csv', index=False)
            return {"status": "success"}
        raise HTTPException(status_code=404, detail="Kayıt bulunamadı")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/history/delete")
async def delete_history(data: dict):
    try:
        df = pd.read_csv('models/history.csv')
        date_to_del = str(data['date'])
        # Tarih sütununu string yaparak kıyasla
        df['date'] = df['date'].astype(str)
        if date_to_del in df['date'].values:
            df = df[df['date'] != date_to_del]
            df.to_csv('models/history.csv', index=False)
            return {"status": "success"}
        raise HTTPException(status_code=404, detail="Kayıt bulunamadı")
    except Exception as e:
        print(f"Delete Error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/rnn/retrain")
async def retrain_rnn():
    try:
        models = load_models()
        df = pd.read_csv('models/history.csv')
        weights = df['weight_kg'].values.astype(np.float32)
        X, y = [], []
        for i in range(len(weights)-7):
            X.append(weights[i:i+7]); y.append(weights[i+7])
        X_tensor = torch.tensor(np.array(X)).unsqueeze(-1).to(device)
        y_tensor = torch.tensor(np.array(y)).unsqueeze(-1).to(device)
        optimizer = torch.optim.Adam(models['rnn'].parameters(), lr=0.01)
        criterion = torch.nn.MSELoss()
        models['rnn'].train()
        for _ in range(30):
            outputs = models['rnn'](X_tensor); loss = criterion(outputs, y_tensor)
            optimizer.zero_grad(); loss.backward(); optimizer.step()
        torch.save(models['rnn'].state_dict(), 'models/rnn_trend_model.pth')
        # Plot
        import matplotlib.pyplot as plt
        models['rnn'].eval()
        with torch.no_grad(): preds = models['rnn'](X_tensor).cpu().numpy()
        plt.figure(figsize=(12, 5))
        plt.plot(weights[7:], label='Gerçek Veri', color='blue', alpha=0.5)
        plt.plot(preds, label='RNN Tahmini', color='red', linestyle='--')
        plt.title('RNN Model Performansı (Tüm Yıl)')
        plt.legend()
        plt.savefig('static/forecast_performance.png')
        plt.close()
        return {"status": "success", "loss": float(loss)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)