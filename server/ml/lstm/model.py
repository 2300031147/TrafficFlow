# import torch
# import torch.nn as nn
import logging

logger = logging.getLogger(__name__)

class TrafficForecastLSTM: # nn.Module
    """
    PyTorch LSTM defining the neural network architecture forecasting 
    the next N minutes of expected demand limits.
    """
    def __init__(self, input_dim: int, hidden_dim: int, num_layers: int, output_dim: int):
        # super().__init__()
        self.input_dim = input_dim
        self.output_dim = output_dim
        # self.lstm = nn.LSTM(input_dim, hidden_dim, num_layers, batch_first=True)
        # self.linear = nn.Linear(hidden_dim, output_dim)

    def forward(self, x):
        # out, _ = self.lstm(x)
        # out = self.linear(out[:, -1, :])
        # return out
        pass

    def save_weights(self, path: str):
        # torch.save(self.state_dict(), path)
        pass

    def load_weights(self, path: str):
        # self.load_state_dict(torch.load(path))
        pass
