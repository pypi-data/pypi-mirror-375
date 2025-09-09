import torch.nn.functional as F

class CosineEmbeddingLoss:
    """Cosine Embedding Loss for similarity learning"""
    def __init__(self, margin=0.0):
        self.margin = margin

    def __call__(self, x1, x2, label):
        return F.cosine_embedding_loss(x1, x2, label, margin=self.margin)
