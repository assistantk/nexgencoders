import torch
import torch.nn as nn
import torch.nn.functional as F

class SatelliteCNN(nn.Module):
    def __init__(self, num_classes=4):
        super(SatelliteCNN, self).__init__()
        # Convolutional layers
        self.conv1 = nn.Conv2d(3, 32, kernel_size=3, padding=1)
        self.conv2 = nn.Conv2d(32, 64, kernel_size=3, padding=1)
        self.conv3 = nn.Conv2d(64, 128, kernel_size=3, padding=1)
        self.pool = nn.MaxPool2d(2, 2)
        
        # Fully connected layers
        # Input size is 64x64, after 3 pools (2x2) it becomes 8x8
        self.fc1 = nn.Linear(128 * 8 * 8, 512)
        self.fc2 = nn.Linear(512, num_classes)
        self.dropout = nn.Dropout(0.25)

    def forward(self, x):
        # x shape: (batch, 3, 64, 64)
        x = self.pool(F.relu(self.conv1(x))) # (batch, 32, 32, 32)
        x = self.pool(F.relu(self.conv2(x))) # (batch, 64, 16, 16)
        x = self.pool(F.relu(self.conv3(x))) # (batch, 128, 8, 8)
        
        x = x.view(-1, 128 * 8 * 8)
        x = self.dropout(F.relu(self.fc1(x)))
        x = self.fc2(x)
        return x
