import torch.nn.functional as F

class TripletLoss:
    """Triplet Margin Loss"""
    def __init__(self, margin=1.0):
        self.margin = margin

    def __call__(self, anchor, positive, negative):
        return F.triplet_margin_loss(anchor, positive, negative, margin=self.margin, reduction='mean')
