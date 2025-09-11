import torch.nn as nn
from arkitwist.blocks import ArkitwistLayer

class ArkitwistModel(nn.Module):
    def __init__(
            self,
            *,
            vocab_size: int,
            num_channels: int = 768,
            num_layers: int = 6,
            num_heads: int = 12,
            head_feats: int = 64,
            elapsic_feats: int = 100,
            hidden_feats: int = 2048,
            device = "cpu"
        ):
        super().__init__()
        self.embedding = nn.Embedding(vocab_size, num_channels, device=device)
        self.core = nn.ModuleList([
            ArkitwistLayer(
                vocab_size=vocab_size,
                num_channels=num_channels,
                num_heads=num_heads,
                head_feats=head_feats,
                elapsic_feats=elapsic_feats,
                hidden_feats=hidden_feats,
                device=device
            ) for _ in range(0, num_layers)
        ])
        self.output = nn.Linear(num_channels, vocab_size, device=device)
    def forward(self, ph, mask):
        x = self.embedding(ph)
        for layer in self.core:
            x = layer(x, ph, mask)
        return x
    def prediction(self, ph, mask):
        return nn.functional.softmax(self.output(self.forward(ph, mask)), dim=-1)