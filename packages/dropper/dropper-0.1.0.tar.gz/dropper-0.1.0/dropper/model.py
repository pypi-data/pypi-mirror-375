import torch
from torch import nn
class Dropper(nn.Module):
    """A model that prevents overfitting using a high-rate dropout layer after the last batch normalization."""
    def __init__(self):
        super().__init__()
        self.conv1 = nn.Sequential(
            nn.Conv2d(in_channels=3,out_channels=32,kernel_size=3,stride=1,padding="same"),
            nn.MaxPool2d(kernel_size=2,stride=2),
            nn.PReLU(),
            nn.BatchNorm2d(32),
        )
        self.conv2 = nn.Sequential(
            nn.Conv2d(32,64,3,1,padding="same"),
            nn.MaxPool2d(kernel_size=2,stride=2),
            nn.PReLU(),
            nn.BatchNorm2d(64),
        )
        self.conv3 = nn.Sequential(
            nn.Conv2d(64,128,3,1,padding="same"),
            nn.PReLU(),
            nn.BatchNorm2d(128),
        )
        self.conv4 = nn.Sequential(
            nn.Conv2d(128, 256, 3, 1, padding="same"),
            nn.PReLU(),
            nn.BatchNorm2d(256),
            nn.Dropout(0.8)
        )
        self.fc1 = nn.Sequential(
            nn.Linear(16384,256),
            nn.PReLU(),
            nn.Linear(256, 128),
            nn.PReLU(),
            nn.Linear(128,10)
        )
    def forward(self, x):
        x = self.conv1(x)
        x = self.conv2(x)
        x = self.conv3(x)
        x = self.conv4(x)
        x = torch.flatten(x,1)
        x = self.fc1(x)
        return x