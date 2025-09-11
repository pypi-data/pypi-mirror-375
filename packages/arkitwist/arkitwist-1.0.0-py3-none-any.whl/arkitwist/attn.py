import torch
import torch.nn as nn
import torch.nn.functional as F
import math

def _softmax_attention(K: torch.Tensor, V: torch.Tensor, mask: torch.Tensor):
    """
    :param K: tensor(float)[B, T, F]
    :param V: tensor(float)[B, T, F]
    :param mask: tensor(bool)[B, T]
    :return: tensor(float)[B, T, F]
    """
    if K.shape[-2] <= 1:
        return V
    detr = math.sqrt(K.shape[-1])
    # Attn: tensor(float)[B, Tq, Tk]
    Attn = K @ K.transpose(1, 2)
    # Filter: tensor(bool)[B, Tq, Tk]
    Filter = torch.logical_or(torch.eye(K.shape[-2], device=K.device, dtype=torch.bool), mask[:, None, :])
    Fixer = torch.all(Filter, dim=-1, keepdim=True)
    # Softmax
    Attn = torch.where(Fixer, 0.0, torch.where(Filter, float("-inf"), Attn / detr))
    Attn = F.softmax(Attn, dim=-1)
    # Apply Attention
    O = torch.where(Fixer, V, Attn @ V)
    return O

def softmax_attention(K: torch.Tensor, V: torch.Tensor, mask: torch.Tensor):
    """
    :param K: tensor(float)[..., T, F]
    :param V: tensor(float)[..., T, F]
    :param mask: tensor(bool)[..., T]
    :return: tensor(float)[..., T, F]
    """
    if K.dim() >= 4:
        ks = K.shape
        return softmax_attention(K.flatten(0, -3), V.flatten(0, -3), mask.flatten(0, -2)).reshape(ks)
    # mask: [B, T]
    ignorate = torch.nonzero(torch.logical_not(torch.all(mask, dim=-1)))[:, 0]
    O = torch.zeros_like(K)
    O[ignorate, :, :] = _softmax_attention(K[ignorate, :, :], V[ignorate, :, :], mask[ignorate, :])
    return O

def calc_bucket_num(t: int):
    return (t - 1).bit_length() - 6

def lsh_attention(K: torch.Tensor, V: torch.Tensor, mask: torch.Tensor):
    """
    :param K: tensor(float)[B, T, F]
    :param V: tensor(float)[B, T, F]
    :param mask: tensor(bool)[B, T]
    :return: tensor(float)[B, T, F]
    """
    lsh_times = calc_bucket_num(K.shape[-2])
    if lsh_times <= 0:
        return _softmax_attention(K, V, mask)
    # Padding tensor
    ipt_len = K.shape[-2]
    if K.shape[-2] % 64 != 0:
        length_diff = 64 - (K.shape[-2] % 64)
        K = F.pad(K.transpose(1, 2), (0, length_diff), 'constant', 0.0).transpose(1, 2)
        V = F.pad(V.transpose(1, 2), (0, length_diff), 'constant', 0.0).transpose(1, 2)
        mask = F.pad(mask[:, None, :], (0, length_diff), 'constant', True)[:, 0, :]
    src_len = K.shape[-2]
    # Set method: [B, T, F] -> [B, 1, T, F], [B, T] -> [B, 1, T]
    K = K[:, None, :, :]
    V = V[:, None, :, :]
    mask = mask[:, None, :]
    # LSH Compute
    lsh_panels = torch.randn(lsh_times, K.shape[0], 1, 1, K.shape[-1], device=K.device)
    for panel in lsh_panels:
        # indice: [B, n, T / n, F]
        indice = torch.argsort(torch.sum(K * panel, dim=-1, keepdim=True), dim=-2).repeat(1, 1, 1, K.shape[-1])
        s = (K.shape[0], K.shape[1] * 2, K.shape[2] // 2, K.shape[3])
        K = torch.gather(K, index=indice, dim=-2).reshape(*s)
        V = torch.gather(V, index=indice, dim=-2).reshape(*s)
        mask = torch.gather(mask, index=indice[:, :, :, 0], dim=-1).reshape(*s[:-1])
    # Remethod: [B, n, T / n, F] -> [B * n, T / n, F] -> Attn
    O = softmax_attention(K, V, mask)
    return O.reshape(-1, src_len, O.shape[-1])[:, :ipt_len, :]

def apply_rope(K: torch.Tensor, alpha):
    Kr, Ki = torch.chunk(K, 2, dim=-1)
    P = torch.arange(0, Kr.shape[-2], device=Kr.device)[:, None] / (2 ** torch.arange(0, Kr.shape[-1], device=Kr.device)[None, :])
    P = P * alpha
    Pr, Pi = torch.cos(P), torch.sin(P)
    return torch.cat([Kr * Pr - Ki * Pi, Kr * Pi + Ki * Pr], dim=-1)

class LSHAttention(nn.Module):
    def __init__(self, num_channels: int, num_heads: int, head_feats: int, device = "cpu"):
        super().__init__()
        assert head_feats % 2 == 0
        self.num_heads = num_heads
        self.head_feats = head_feats
        self.K = nn.Linear(num_channels, num_heads * head_feats, device=device)
        self.V = nn.Linear(num_channels, num_heads * head_feats, device=device)
        self.rope_alpha = nn.Parameter(torch.ones(num_heads * head_feats // 2, device=device), requires_grad=True)
    def forward(self, x, mask):
        K = self.K(x).unflatten(-1, (self.num_heads, self.head_feats)).transpose(1, 2)
        K = apply_rope(K, self.rope_alpha.reshape(self.num_heads, self.head_feats // 2)[None, :, None, :]).flatten(0, 1)
        V = self.V(x).unflatten(-1, (self.num_heads, self.head_feats)).transpose(1, 2).flatten(0, 1)
        mask = mask.unsqueeze(1).repeat(1, self.num_heads, 1).flatten(0, 1)
        O = lsh_attention(K, V, mask)
        return O.unflatten(0, (x.shape[0], self.num_heads)).transpose(1, 2).flatten(-2, -1)