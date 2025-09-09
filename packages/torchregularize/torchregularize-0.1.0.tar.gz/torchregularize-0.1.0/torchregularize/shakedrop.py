import torch
import torch.nn as nn

class ShakeDrop(nn.Module):
    """
    ShakeDrop regularization.
    Randomly scales residual branches with random multipliers.
    """
    def __init__(self, p_drop=0.5):
        super().__init__()
        self.p_drop = p_drop

    def forward(self, x, residual):
        if not self.training:
            return x + residual

        if torch.rand(1).item() < self.p_drop:
            alpha = torch.empty(1).uniform_(-1, 1).to(x.device)
            beta = torch.empty(1).uniform_(0, 1).to(x.device)
            return x + beta * residual + alpha * residual.detach()
        else:
            return x + residual
