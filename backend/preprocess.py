import os
import librosa
import numpy as np
import torch
import joblib
from sklearn.preprocessing import StandardScaler

# Genres list
GENRES = ['blues', 'classical', 'country', 'disco', 'hiphop', 'jazz', 'metal', 'pop', 'reggae', 'rock']
DATA_PATH = "data"

def extract_features(audio_path):
    try:
        y, sr = librosa.load(audio_path, duration=30)
        
        # MFCC (20)
        mfcc = librosa.feature.mfcc(y=y, sr=sr, n_mfcc=20)
        mfcc_mean = np.mean(mfcc.T, axis=0)
        mfcc_std = np.std(mfcc.T, axis=0)
        
        # Chroma
        chroma = np.mean(librosa.feature.chroma_stft(y=y, sr=sr).T, axis=0)
        
        # Spectral Centroid
        spectral_centroid = np.mean(librosa.feature.spectral_centroid(y=y, sr=sr).T, axis=0)
        
        # RMSE
        rmse = np.mean(librosa.feature.rms(y=y).T, axis=0)
        
        # Zero Crossing Rate
        zcr = np.mean(librosa.feature.zero_crossing_rate(y=y).T, axis=0)
        
        # Concatenate all features
        features = np.concatenate([
            mfcc_mean, 
            mfcc_std, 
            chroma, 
            spectral_centroid, 
            rmse, 
            zcr
        ])
        return features
    except Exception as e:
        print(f"Error processing {audio_path}: {e}")
        return None

if __name__ == "__main__":
    X, y = [], []
    
    for i, genre in enumerate(GENRES):
        genre_path = os.path.join(DATA_PATH, genre)
        print(f"Processing: {genre}...")
        for filename in os.listdir(genre_path):
            if filename.endswith(".wav"):
                file_path = os.path.join(genre_path, filename)
                feat = extract_features(file_path)
                if feat is not None:
                    X.append(feat)
                    y.append(i)

    X = np.array(X)
    y = np.array(y)

    print(f"Features shape: {X.shape}")
    
    # Scale features
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)
    
    # Save artifacts
    np.save("X_scaled.npy", X_scaled)
    np.save("y.npy", y)
    joblib.dump(scaler, "scaler.joblib")
    
    print("Pre-processing complete! Files saved: X_scaled.npy, y.npy, scaler.joblib")
