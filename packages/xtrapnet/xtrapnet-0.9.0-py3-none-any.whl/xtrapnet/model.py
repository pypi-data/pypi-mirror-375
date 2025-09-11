import torch
import torch.nn as nn
import torch.nn.functional as F

class XtrapNet(nn.Module):
    def __init__(self, input_dim, dropout_rate=0.1):
        super(XtrapNet, self).__init__()
        self.fc1 = nn.Linear(input_dim, 64)
        self.fc2 = nn.Linear(64, 64)
        self.fc3 = nn.Linear(64, 1)
        self.dropout = nn.Dropout(dropout_rate)

    def forward(self, x, mc_dropout=False):
        x = F.relu(self.fc1(x))
        x = self.dropout(x) if mc_dropout else x
        x = F.relu(self.fc2(x))
        x = self.dropout(x) if mc_dropout else x
        x = self.fc3(x)
        return x

    def predict(self, features, mc_dropout=False, n_samples=10):
        self.eval()
        features = torch.from_numpy(features).float()
        with torch.no_grad():
            if mc_dropout:
                preds = torch.stack([
                    self.forward(features, mc_dropout=True) for _ in range(n_samples)
                ])
                return preds.mean(dim=0).numpy(), preds.var(dim=0).numpy()
            else:
                return self.forward(features).numpy()
