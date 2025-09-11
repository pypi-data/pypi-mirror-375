import torch
import torch.nn as nn
import torch.nn.functional as F
from arkitwist.attn import LSHAttention

class TimeElapsic(nn.Module):
    def __init__(self, num_channels: int, elapsic_dim: int, device = "cpu"):
        super().__init__()
        self.premix = nn.Parameter(torch.rand(num_channels, device=device), requires_grad=True)
        self.postmix = nn.Sequential(
            nn.Linear(num_channels, elapsic_dim, device=device),
            nn.SiLU(),
            nn.Linear(elapsic_dim, num_channels, device=device),
            nn.Sigmoid()
        )
    def forward(self, x):
        tx = torch.zeros_like(x)
        tx[:, 1:, :] = x[:, :-1, :]
        dx = tx - x
        return x + dx * self.postmix(x + dx * self.premix)

class ArkitwistLayer(nn.Module):
    def __init__(self, vocab_size: int, num_channels: int, num_heads: int, head_feats: int, elapsic_feats: int, hidden_feats: int, device = "cpu"):
        super().__init__()
        self.elapse1 = TimeElapsic(num_channels, elapsic_feats, device=device)
        self.attn = LSHAttention(num_channels, num_heads, head_feats, device=device)
        self.norm1 = nn.LayerNorm(num_channels, device=device)
        self.elapse2 = TimeElapsic(num_channels, elapsic_feats, device=device)
        self.deepembed = nn.Embedding(vocab_size, num_channels, device=device)
        nn.init.ones_(self.deepembed.weight)
        self.mlp = nn.Sequential(
            nn.Linear(num_channels, hidden_feats, device=device),
            nn.GELU(),
            nn.Linear(hidden_feats, num_channels, device=device)
        )
        self.norm2 = nn.LayerNorm(num_channels)
    def forward(self, x, ph, mask):
        x = self.norm1(x + self.attn(self.elapse1(x), mask))
        x = self.norm2(x + self.mlp(self.elapse2(x)) * self.deepembed(ph))
        return x

