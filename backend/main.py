from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
import torch
import torch.nn as nn
import librosa
import numpy as np
import io
import joblib

app = FastAPI()
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

# Improved ANN Architecture (Must match train.py)
class MusicANN(nn.Module):
    def __init__(self, input_size, num_classes):
        super(MusicANN, self).__init__()
        self.network = nn.Sequential(
            nn.Linear(input_size, 512),
            nn.BatchNorm1d(512),
            nn.ReLU(),
            nn.Dropout(0.35),
            
            nn.Linear(512, 256),
            nn.BatchNorm1d(256),
            nn.ReLU(),
            nn.Dropout(0.35),
            
            nn.Linear(256, 128),
            nn.BatchNorm1d(128),
            nn.ReLU(),
            nn.Dropout(0.35),
            
            nn.Linear(128, num_classes)
        )
    def forward(self, x):
        return self.network(x)

GENRES = ['Blues', 'Classical', 'Country', 'Disco', 'Hiphop', 'Jazz', 'Metal', 'Pop', 'Reggae', 'Rock']

# Load Model and Scaler
try:
    scaler = joblib.load("scaler.joblib")
    input_size = scaler.mean_.shape[0]
    model = MusicANN(input_size, 10)
    model.load_state_dict(torch.load("music_ann.pth", map_location=torch.device('cpu')))
    model.eval()
    print(f"Model and Scaler loaded successfully. (Input Size: {input_size})")
except Exception as e:
    print(f"Error: Could not load Model or Scaler! {e}")

def extract_features_inference(y, sr):
    # mfcc (20)
    mfcc = librosa.feature.mfcc(y=y, sr=sr, n_mfcc=20)
    mfcc_mean = np.mean(mfcc.T, axis=0)
    mfcc_std = np.std(mfcc.T, axis=0)
    
    # chroma
    chroma = np.mean(librosa.feature.chroma_stft(y=y, sr=sr).T, axis=0)
    
    # spectral centroid
    spectral_centroid = np.mean(librosa.feature.spectral_centroid(y=y, sr=sr).T, axis=0)
    
    # rmse
    rmse = np.mean(librosa.feature.rms(y=y).T, axis=0)
    
    # zcr
    zcr = np.mean(librosa.feature.zero_crossing_rate(y=y).T, axis=0)
    
    features = np.concatenate([mfcc_mean, mfcc_std, chroma, spectral_centroid, rmse, zcr])
    return features

@app.post("/predict")
async def predict(file: UploadFile = File(...)):
    content = await file.read()
    y, sr = librosa.load(io.BytesIO(content), duration=30)
    
    # Feature Extraction
    feat = extract_features_inference(y, sr)
    
    # Normalization
    feat_scaled = scaler.transform(feat.reshape(1, -1))
    
    # Prediction
    features_tensor = torch.tensor(feat_scaled).float()
    
    with torch.no_grad():
        output = model(features_tensor)
        probabilities = torch.nn.functional.softmax(output, dim=1)
        confidence, prediction = torch.max(probabilities, dim=1)
    
    return {
        "genre": GENRES[prediction.item()],
        "confidence": f"{confidence.item()*100:.2f}%"
    }