import torch
import torch.nn as nn
import torch.nn.functional as F

class DropBlock2D(nn.Module):
    """
    DropBlock for 2D feature maps (CNNs).
    Randomly zeros out contiguous regions of feature maps.
    """
    def __init__(self, block_size=3, drop_prob=0.1):
        super().__init__()
        self.block_size = block_size
        self.drop_prob = drop_prob

    def forward(self, x):
        if not self.training or self.drop_prob == 0.0:
            return x

        gamma = self.drop_prob * x.numel() / (self.block_size ** 2 * x.shape[0] * x.shape[1] * x.shape[2] * x.shape[3])
        mask = (torch.rand(x.shape[0], *x.shape[2:], device=x.device) < gamma).float()
        mask = F.max_pool2d(mask.unsqueeze(1), kernel_size=self.block_size, stride=1, padding=self.block_size // 2)
        mask = 1 - mask
        return x * mask
