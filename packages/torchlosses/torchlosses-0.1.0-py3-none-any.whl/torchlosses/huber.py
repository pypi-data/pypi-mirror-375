import torch
import torch.nn as nn

class HuberLoss(nn.Module):
    """Huber Loss (a.k.a. Smooth L1)"""
    def __init__(self, delta=1.0, reduction='mean'):
        super().__init__()
        self.delta = delta
        self.reduction = reduction

    def forward(self, inputs, targets):
        diff = torch.abs(inputs - targets)
        loss = torch.where(diff < self.delta, 0.5 * diff**2, self.delta * (diff - 0.5 * self.delta))
        return loss.mean() if self.reduction == 'mean' else loss.sum()
