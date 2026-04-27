import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import DataLoader, Dataset
import numpy as np
from model import SatelliteCNN
import os

# Dummy dataset for training purposes (to make it runnable without external data)
class DummySatelliteDataset(Dataset):
    def __init__(self, size=100, img_size=(3, 64, 64)):
        self.size = size
        self.img_size = img_size
        self.data = torch.randn(size, *img_size)
        self.labels = torch.randint(0, 4, (size,))

    def __len__(self):
        return self.size

    def __getitem__(self, idx):
        return self.data[idx], self.labels[idx]

def train_model():
    # Parameters
    num_classes = 4
    batch_size = 16
    epochs = 5
    learning_rate = 0.001

    # Initialize model, loss, and optimizer
    model = SatelliteCNN(num_classes=num_classes)
    criterion = nn.CrossEntropyLoss()
    optimizer = optim.Adam(model.parameters(), lr=learning_rate)

    # Data loaders
    train_dataset = DummySatelliteDataset(size=200)
    train_loader = DataLoader(train_dataset, batch_size=batch_size, shuffle=True)

    print("Starting training...")
    for epoch in range(epochs):
        model.train()
        running_loss = 0.0
        for i, (images, labels) in enumerate(train_loader):
            optimizer.zero_grad()
            outputs = model(images)
            loss = criterion(outputs, labels)
            loss.backward()
            optimizer.step()
            running_loss += loss.item()

        print(f"Epoch [{epoch+1}/{epochs}], Loss: {running_loss/len(train_loader):.4f}")

    # Save the model
    save_path = os.path.join(os.path.dirname(__file__), "satellite_model.pth")
    torch.save(model.state_dict(), save_path)
    print(f"Model saved to {save_path}")

if __name__ == "__main__":
    train_model()
