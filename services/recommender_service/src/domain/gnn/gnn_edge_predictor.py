import torch
from torch import nn
from torch_geometric.nn import SAGEConv


class GNNEdgeLabelPredictor(nn.Module):
    def __init__(self, in_channels, hidden_channels, out_channels):
        super().__init__()
        self.in_channels = in_channels
        self.hidden_channels = hidden_channels
        self.out_channels = out_channels
        
        self.conv1 = SAGEConv(in_channels, hidden_channels)
        self.conv2 = SAGEConv(hidden_channels, out_channels)
        self.relu = nn.ReLU()
        self.predictor = nn.Sequential(
            nn.Linear(out_channels*2, hidden_channels),
            nn.ReLU(),
            nn.Dropout(0.5),
            nn.Linear(hidden_channels, 1)
        )

    def encode(self, x, edge_index):
        x = self.conv1(x, edge_index)
        x = self.relu(x)
        x = self.conv2(x, edge_index)
        return x

    def decode(self, z, edge_label_index):
        src = z[edge_label_index[0]]
        dst = z[edge_label_index[1]]
        return self.predictor(torch.cat([src, dst], dim=1)).squeeze()

    def forward(self, x, edge_index, edge_label_index):
        z = self.encode(x, edge_index)
        return self.decode(z, edge_label_index)
    
    def save(self, filepath):
        torch.save({
            "state_dict": self.state_dict(),
            "in_channels": self.in_channels,
            "hidden_channels": self.hidden_channels,
            "out_channels": self.out_channels
        }, filepath)

    def load_weights(self, filepath, device="cpu"):
        """
        Charge les poids du checkpoint dans l'instance existante.
        """
        checkpoint = torch.load(filepath, map_location=device)
        self.load_state_dict(checkpoint["state_dict"])
        self.to(device)
        self.eval()

    @classmethod
    def load(cls, filepath, device="cpu"):
        checkpoint = torch.load(filepath, map_location=device)

        model = cls(
            checkpoint["in_channels"],
            checkpoint["hidden_channels"],
            checkpoint["out_channels"]
        )
        model.load_state_dict(checkpoint["state_dict"])
        model.to(device)
        model.eval()

        return model
    