import torch
import torch.nn as nn
import torch.nn.functional as F

class ContrastiveLoss(nn.Module):
    """Contrastive Loss for Siamese networks"""
    def __init__(self, margin=1.0):
        super().__init__()
        self.margin = margin

    def forward(self, x1, x2, label):
        dist = F.pairwise_distance(x1, x2)
        loss = (1 - label) * torch.pow(dist, 2) + label * torch.pow(torch.clamp(self.margin - dist, min=0.0), 2)
        return loss.mean()
