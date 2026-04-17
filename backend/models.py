import torch
import torch.nn as nn
from torchvision import models

class RecyclingClassifier(nn.Module):
    def __init__(self, num_classes=6):
        super(RecyclingClassifier, self).__init__()
        # Backbone (Fine-tuned ResNet18)
        self.resnet = models.resnet18(pretrained=True)
        self.feature_dim = self.resnet.fc.in_features
        self.resnet.fc = nn.Identity() 
        
        # Fine-tune only deeper layers
        for name, param in self.resnet.named_parameters():
            if "layer4" in name or "layer3" in name:
                param.requires_grad = True
            else:
                param.requires_grad = False

        # Single Classification Head
        self.classifier = nn.Sequential(
            nn.Linear(self.feature_dim, 512),
            nn.BatchNorm1d(512),
            nn.ReLU(),
            nn.Dropout(0.4),
            nn.Linear(512, 256),
            nn.ReLU(),
            nn.Dropout(0.3),
            nn.Linear(256, num_classes)
        )

    def forward(self, x, return_features=False):
        features = self.resnet(x)
        if return_features:
            return features
        logits = self.classifier(features)
        return logits

# NEW: RNN Trend Analysis Modeli
class RecycleTrendRNN(nn.Module):
    def __init__(self, input_dim=1, hidden_dim=64, num_layers=2):
        super(RecycleTrendRNN, self).__init__()
        # Input: [Batch, Sequence (7 days), Weight_per_day]
        self.lstm = nn.LSTM(input_dim, hidden_dim, num_layers, batch_first=True)
        self.fc = nn.Linear(hidden_dim, 1) # Output: Next week/month predicted weight

    def forward(self, x):
        # x shape: (batch, seq_len, 1)
        out, _ = self.lstm(x)
        out = self.fc(out[:, -1, :])
        return out
