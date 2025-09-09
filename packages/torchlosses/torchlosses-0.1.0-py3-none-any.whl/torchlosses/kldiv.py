import torch.nn as nn
import torch.nn.functional as F

class KLDivLoss(nn.Module):
    """Kullback-Leibler Divergence Loss"""
    def __init__(self, reduction='batchmean'):
        super().__init__()
        self.reduction = reduction

    def forward(self, inputs, targets):
        return F.kl_div(inputs, targets, reduction=self.reduction)
