import os
import torch
from torchvision import transforms
from torch.utils.data import Dataset, DataLoader
from PIL import Image

class RecyclingDataset(Dataset):
    def __init__(self, data_dir, txt_file=None, image_size=224, transform=None):
        self.data_dir = data_dir
        self.image_size = image_size
        self.transform = transform
        
        self.samples = []
        self.idx_to_class = {
            1: 'glass', 2: 'paper', 3: 'cardboard',
            4: 'plastic', 5: 'metal', 6: 'trash'
        }

        if txt_file and os.path.exists(os.path.join(data_dir, txt_file)):
            with open(os.path.join(data_dir, txt_file), 'r') as f:
                for line in f:
                    parts = line.strip().split()
                    if len(parts) >= 2:
                        img_name = parts[0]
                        label = int(parts[1])
                        cls_folder = self.idx_to_class[label]
                        img_path = os.path.join(data_dir, cls_folder, img_name)
                        if os.path.exists(img_path):
                            self.samples.append((img_path, label - 1)) # 0-indexed

        self.classes = ['glass', 'paper', 'cardboard', 'plastic', 'metal', 'trash']

    def __len__(self):
        return len(self.samples)

    def __getitem__(self, idx):
        img_path, label = self.samples[idx]
        image = Image.open(img_path).convert('RGB')
        
        if self.transform:
            image = self.transform(image)
        else:
            to_tensor = transforms.Compose([
                transforms.Resize((self.image_size, self.image_size)),
                transforms.ToTensor(),
                transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])
            ])
            image = to_tensor(image)
            
        return image, torch.tensor(label)

def get_recycling_dataloaders(data_dir, batch_size=32):
    train_transform = transforms.Compose([
        transforms.Resize((224, 224)),
        transforms.RandomHorizontalFlip(),
        transforms.RandomRotation(15),
        transforms.ColorJitter(brightness=0.2, contrast=0.2),
        transforms.ToTensor(),
        transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])
    ])
    
    val_transform = transforms.Compose([
        transforms.Resize((224, 224)),
        transforms.ToTensor(),
        transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])
    ])

    train_ds = RecyclingDataset(data_dir, txt_file="one-indexed-files-notrash_train.txt", transform=train_transform)
    val_ds = RecyclingDataset(data_dir, txt_file="one-indexed-files-notrash_val.txt", transform=val_transform)
    
    train_loader = DataLoader(train_ds, batch_size=batch_size, shuffle=True)
    val_loader = DataLoader(val_ds, batch_size=batch_size, shuffle=False)
    
    return train_loader, val_loader, train_ds.classes
