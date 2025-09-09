import torch
import torch.nn as nn

class StochasticDepth(nn.Module):
    """
    Stochastic Depth regularization (a.k.a. DropPath).
    Randomly skips residual branches during training.
    """
    def __init__(self, survival_prob=0.8):
        super().__init__()
        self.survival_prob = survival_prob

    def forward(self, x, residual):
        if not self.training or torch.rand(1).item() < self.survival_prob:
            return x + residual
        else:
            return x
