import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import DataLoader, TensorDataset
from sklearn.model_selection import train_test_split
import numpy as np
import os

# Improved ANN Architecture
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

def train_model():
    if not os.path.exists("X_scaled.npy") or not os.path.exists("y.npy"):
        print("Error: Pre-processing files (X_scaled.npy, y.npy) not found! Please run preprocess.py first.")
        return

    # Load Data
    X = np.load("X_scaled.npy")
    y = np.load("y.npy")
    
    # Train/Val Split
    X_train, X_val, y_train, y_val = train_test_split(X, y, test_size=0.15, random_state=42, stratify=y)
    
    # Convert to Tensors
    train_ds = TensorDataset(torch.tensor(X_train).float(), torch.tensor(y_train).long())
    val_ds = TensorDataset(torch.tensor(X_val).float(), torch.tensor(y_val).long())
    
    train_loader = DataLoader(train_ds, batch_size=32, shuffle=True)
    val_loader = DataLoader(val_ds, batch_size=32)
    
    # Model Setup
    model = MusicANN(X.shape[1], 10)
    criterion = nn.CrossEntropyLoss()
    optimizer = optim.Adam(model.parameters(), lr=0.001, weight_decay=1e-5)
    scheduler = optim.lr_scheduler.ReduceLROnPlateau(optimizer, mode='max', factor=0.5, patience=10)
    
    best_acc = 0
    epochs = 200
    
    print(f"Training started... (Features: {X.shape[1]}, Samples: {len(X_train)})")
    for epoch in range(epochs):
        model.train()
        train_loss = 0
        for batch_x, batch_y in train_loader:
            optimizer.zero_grad()
            outputs = model(batch_x)
            loss = criterion(outputs, batch_y)
            loss.backward()
            optimizer.step()
            train_loss += loss.item()
            
        # Validation
        model.eval()
        val_correct = 0
        val_total = 0
        with torch.no_grad():
            for batch_x, batch_y in val_loader:
                outputs = model(batch_x)
                _, predicted = torch.max(outputs.data, 1)
                val_total += batch_y.size(0)
                val_correct += (predicted == batch_y).sum().item()
        
        val_acc = 100 * val_correct / val_total
        scheduler.step(val_acc)
        
        if (epoch+1) % 20 == 0 or val_acc > best_acc:
            print(f"Epoch [{epoch+1}/{epochs}], Loss: {train_loss/len(train_loader):.4f}, Val Acc: {val_acc:.2f}%")
        
        # Save Best Model
        if val_acc > best_acc:
            best_acc = val_acc
            torch.save(model.state_dict(), "music_ann.pth")
            
    print(f"Training Complete! Best Validation Accuracy: {best_acc:.2f}%")

if __name__ == "__main__":
    train_model()