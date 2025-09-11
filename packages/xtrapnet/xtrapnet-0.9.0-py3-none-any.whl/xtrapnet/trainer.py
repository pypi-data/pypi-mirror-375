import torch
from torch.utils.data import Dataset, DataLoader

class XtrapDataset(Dataset):
    def __init__(self, labels, features):
        super(XtrapDataset, self).__init__()
        self.labels = labels
        self.features = features

    def __len__(self):
        return self.features.shape[0]

    def __getitem__(self, idx):
        return {'feature': self.features[idx], 'label': self.labels[idx]}

class XtrapTrainer:
    def __init__(self, network, learning_rate=0.01, num_epochs=1000, batch_size=100):
        self.network = network
        self.learning_rate = learning_rate
        self.num_epochs = num_epochs
        self.batch_size = batch_size
        self.optimizer = torch.optim.Adam(self.network.parameters(), lr=self.learning_rate)
        self.criterion = torch.nn.MSELoss()

    def train(self, labels, features):
        self.network.train()
        dataset = XtrapDataset(labels, features)
        loader = DataLoader(dataset, shuffle=True, batch_size=self.batch_size)
        for epoch in range(self.num_epochs):
            self.train_epoch(loader)

    def train_epoch(self, loader):
        total_loss = 0.0
        for i, data in enumerate(loader):
            features = data['feature'].float()
            labels = data['label'].float()
            self.optimizer.zero_grad()
            predictions = self.network(features)
            loss = self.criterion(predictions, labels)
            loss.backward()
            self.optimizer.step()
            total_loss += loss.item()
