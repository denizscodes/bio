import os
import torch
import torch.nn as nn
import torch.optim as optim
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
import joblib
import ssl
import pandas as pd
from sklearn.metrics import confusion_matrix, roc_curve, auc
from sklearn.neighbors import NearestNeighbors
from tqdm import tqdm

ssl._create_default_https_context = ssl._create_unverified_context
from data_manager import get_recycling_dataloaders
from models import RecyclingClassifier, RecycleTrendRNN

def generate_synthetic_history():
    print("Generating 1-year synthetic recycling history...")
    dates = pd.date_range(end=pd.Timestamp.now(), periods=365)
    # Her gün için rastgele atık miktarı (0-5kg arası)
    data = {
        'date': dates,
        'weight_kg': np.random.uniform(0.1, 5.0, size=365) * (1 + 0.5 * np.sin(np.linspace(0, 4*np.pi, 365))) # Mevsimsel dalgalanma ekle
    }
    df = pd.DataFrame(data)
    df.to_csv('models/history.csv', index=False)
    return df

def train_rnn(history_df, device):
    print("Training RNN Trend Analysis Model...")
    weights = history_df['weight_kg'].values.astype(np.float32)
    
    # 7 günlük pencere kullanarak sıradaki günü tahmin etme
    X, y = [], []
    for i in range(len(weights)-7):
        X.append(weights[i:i+7])
        y.append(weights[i+7])
    
    X = torch.tensor(np.array(X)).unsqueeze(-1).to(device) # (N, 7, 1)
    y = torch.tensor(np.array(y)).unsqueeze(-1).to(device)
    
    rnn = RecycleTrendRNN().to(device)
    optimizer = optim.Adam(rnn.parameters(), lr=0.01)
    criterion = nn.MSELoss()
    
    for epoch in range(50):
        rnn.train()
        outputs = rnn(X)
        loss = criterion(outputs, y)
        optimizer.zero_grad()
        loss.backward()
        optimizer.step()
    
    torch.save(rnn.state_dict(), 'models/rnn_trend_model.pth')
    print("RNN Training Complete.")

def train():
    DATA_DIR = "data"
    MODELS_DIR = "models"
    STATIC_DIR = "static"
    os.makedirs(MODELS_DIR, exist_ok=True)
    os.makedirs(STATIC_DIR, exist_ok=True)
    
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    if torch.backends.mps.is_available(): device = torch.device("mps")
    print(f"Device: {device}")

    # 1. Classification Model
    train_loader, val_loader, classes = get_recycling_dataloaders(DATA_DIR, batch_size=32)
    model = RecyclingClassifier(len(classes)).to(device)
    
    # ... (Hızlı eğitim için önceden eğitilmiş model varsa yükle veya kısa tut)
    # NOT: Kullanıcı "metrikleri düzelt" dediği için tam bir eğitim yapıyoruz.
    criterion = nn.CrossEntropyLoss()
    optimizer = optim.AdamW(model.parameters(), lr=1e-4)
    
    best_acc = 0
    for epoch in range(5): # Hız için 5 epoch
        model.train()
        for imgs, labels in tqdm(train_loader, desc=f"Epoch {epoch+1}/5"):
            imgs, labels = imgs.to(device), labels.to(device)
            outputs = model(imgs)
            loss = criterion(outputs, labels)
            optimizer.zero_grad()
            loss.backward()
            optimizer.step()
        
        # Eval
        model.eval()
        correct, total = 0, 0
        with torch.no_grad():
            for imgs, labels in val_loader:
                imgs, labels = imgs.to(device), labels.to(device)
                outputs = model(imgs)
                _, pred = torch.max(outputs, 1)
                total += labels.size(0)
                correct += (pred == labels).sum().item()
        acc = 100 * correct / total
        print(f"Val Acc: {acc:.2f}%")
        if acc > best_acc:
            best_acc = acc
            torch.save(model.state_dict(), os.path.join(MODELS_DIR, "recycle_model.pth"))

    # 2. KNN Similarity Training
    print("Indexing features for KNN Similarity...")
    model.load_state_dict(torch.load(os.path.join(MODELS_DIR, "recycle_model.pth")))
    model.eval()
    
    all_features = []
    all_labels_for_db = []
    with torch.no_grad():
        for imgs, labels in train_loader:
            feats = model(imgs.to(device), return_features=True)
            all_features.append(feats.cpu().numpy())
            all_labels_for_db.extend(labels.numpy())
    
    X_features = np.concatenate(all_features)
    y_labels = np.array(all_labels_for_db)
    
    knn = NearestNeighbors(n_neighbors=5, metric='cosine')
    knn.fit(X_features)
    
    joblib.dump(knn, os.path.join(MODELS_DIR, "knn_similarity.pkl"))
    joblib.dump(X_features, os.path.join(MODELS_DIR, "features_db.pkl"))
    joblib.dump(y_labels, os.path.join(MODELS_DIR, "labels_db.pkl"))
    joblib.dump(classes, os.path.join(MODELS_DIR, "classes.pkl"))

    # 3. RNN History & Trend
    history_df = generate_synthetic_history()
    train_rnn(history_df, device)

    # Final Evaluation for metrics
    print("Collecting metrics for plots...")
    model.eval()
    all_labels, all_probs = [], []
    with torch.no_grad():
        for imgs, labels in val_loader:
            imgs = imgs.to(device)
            outputs = model(imgs)
            probs = torch.softmax(outputs, dim=1)
            all_labels.extend(labels.numpy())
            all_probs.extend(probs.cpu().numpy())

    # Generate Corrected Metrics
    print("Generating Final Plots...")
    y_true = np.array(all_labels)
    y_probs = np.array(all_probs)
    y_pred = np.argmax(y_probs, axis=1)

    # 1. Classification Report & F1 Plot
    from sklearn.metrics import classification_report
    report = classification_report(y_true, y_pred, target_names=classes, output_dict=True)
    
    metrics_to_plot = ['precision', 'recall', 'f1-score']
    class_metrics = {cls: [report[cls][m] for m in metrics_to_plot] for cls in classes}
    
    x = np.arange(len(metrics_to_plot))
    width = 0.12
    plt.figure(figsize=(10, 6))
    for i, cls in enumerate(classes):
        plt.bar(x + i*width, class_metrics[cls], width, label=cls)
    
    plt.ylabel('Score')
    plt.title('Performance Metrics per Class')
    plt.xticks(x + width*2.5, metrics_to_plot)
    plt.legend(loc='lower left', bbox_to_anchor=(1, 0.5))
    plt.tight_layout()
    plt.savefig(os.path.join(STATIC_DIR, "metrics_score.png"))
    plt.close()

    # 2. CM
    cm = confusion_matrix(y_true, y_pred)
    plt.figure(figsize=(10, 8))
    sns.heatmap(cm, annot=True, fmt='d', cmap='Greens', xticklabels=classes, yticklabels=classes)
    plt.title(f"Confusion Matrix (Accuracy: {best_acc:.2f}%)")
    plt.savefig(os.path.join(STATIC_DIR, "confusion_matrix.png"))
    plt.close()

    # 3. ROC (Recyclable vs Non-Recyclable)
    y_binary_true = (y_true < 5).astype(int)
    y_binary_scores = np.sum(y_probs[:, :5], axis=1)
    fpr, tpr, _ = roc_curve(y_binary_true, y_binary_scores)
    roc_auc = auc(fpr, tpr)

    plt.figure(figsize=(8, 6))
    plt.plot(fpr, tpr, color='forestgreen', lw=2, label=f'ROC curve (area = {roc_auc:.2f})')
    plt.plot([0, 1], [0, 1], color='navy', lw=2, linestyle='--')
    plt.xlabel('False Positive Rate')
    plt.ylabel('True Positive Rate')
    plt.title('Recyclability Identification (ROC)')
    plt.legend(loc="lower right")
    plt.savefig(os.path.join(STATIC_DIR, "roc_curve.png"))
    plt.close()

    print(f"Training Done. Best Acc: {best_acc:.2f}%, ROC AUC: {roc_auc:.2f}")

if __name__ == "__main__":
    train()