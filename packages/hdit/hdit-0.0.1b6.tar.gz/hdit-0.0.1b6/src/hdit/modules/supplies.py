from typing import Optional
import math
from functools import reduce
import torch
from torch import nn
from torch.nn import init
from torch.nn import functional as F
from einops import rearrange
from . import flops, flags


class Swish(nn.Module):
    def forward(self, x):
        return x * torch.sigmoid(x)


class ContinuityEmbedding(nn.Module):
    def __init__(self, total, d_model, dim):
        assert d_model % 2 == 0
        super().__init__()
        emb = torch.arange(0, d_model, step=2) / d_model * math.log(10000)
        emb = torch.exp(-emb)
        pos = torch.arange(total).float()
        emb = pos[:, None] * emb[None, :]
        assert list(emb.shape) == [total, d_model // 2]
        emb = torch.stack([torch.sin(emb), torch.cos(emb)], dim=-1)
        assert list(emb.shape) == [total, d_model // 2, 2]
        emb = emb.view(total, d_model)

        self.embedding = nn.Sequential(
            nn.Embedding.from_pretrained(emb),
            nn.Linear(d_model, dim),
            Swish(),
            nn.Linear(dim, dim),
        )
        self.initialize()

    def initialize(self):
        for module in self.modules():
            if isinstance(module, nn.Linear):
                init.xavier_uniform_(module.weight)
                init.zeros_(module.bias)

    def forward(self, x):
        emb = self.embedding(x)
        return emb


class DiscretenessEmbedding(nn.Module):
    def __init__(self, total, d_model, dim):
        assert d_model % 2 == 0
        super().__init__()
        self.embedding = nn.Sequential(
            nn.Embedding(num_embeddings=total + 1, embedding_dim=d_model, padding_idx=0),
            nn.Linear(d_model, dim),
            Swish(),
            nn.Linear(dim, dim),
        )

    def forward(self, x):
        emb = self.embedding(x)
        return emb


def apply_wd(module):
    for name, param in module.named_parameters():
        if name.endswith("weight"):
            tag_param(param, "wd")
    return module


def zero_init(layer):
    nn.init.zeros_(layer.weight)
    if layer.bias is not None:
        nn.init.zeros_(layer.bias)
    return layer


# Param tags
def tag_param(param, tag):
    if not hasattr(param, "_tags"):
        param._tags = set([tag])
    else:
        param._tags.add(tag)
    return param


def tag_module(module, tag):
    for param in module.parameters():
        tag_param(param, tag)
    return module


@flags.compile_wrap
def rms_norm(x, scale, eps):
    dtype = reduce(torch.promote_types, (x.dtype, scale.dtype, x.dtype))
    mean_sq = torch.mean(x.to(dtype) ** 2, dim=-1, keepdim=True)
    scale = scale.to(dtype) * torch.rsqrt(mean_sq + eps)
    return x * scale.to(x.dtype)


# Kernels
@flags.compile_wrap
def linear_geglu(x, weight, bias=None):
    x = x @ weight.mT
    if bias is not None:
        x = x + bias
    x, gate = x.chunk(2, dim=-1)
    return x * F.gelu(gate)


@flags.compile_wrap
def _apply_rotary_emb_inplace(x, theta, conj):
    dtype = reduce(torch.promote_types, (x.dtype, theta.dtype, torch.float32))
    d = theta.shape[-1]
    assert d * 2 <= x.shape[-1]
    x1, x2 = x[..., :d], x[..., d : d * 2]
    x1_, x2_, theta = x1.to(dtype), x2.to(dtype), theta.to(dtype)
    cos, sin = torch.cos(theta), torch.sin(theta)
    sin = -sin if conj else sin
    y1 = x1_ * cos - x2_ * sin
    y2 = x2_ * cos + x1_ * sin
    x1.copy_(y1)
    x2.copy_(y2)


class ApplyRotaryEmbeddingInplace(torch.autograd.Function):
    generate_vmap_rule = True

    @staticmethod
    def setup_context(ctx, inputs, output):
        x, theta, conj = inputs
        ctx.mark_dirty(x)
        ctx.save_for_backward(theta)
        ctx.save_for_forward(theta)
        ctx.conj = conj

    @staticmethod
    def forward(x, theta, conj):
        _apply_rotary_emb_inplace(x, theta, conj)
        return x

    @staticmethod
    def backward(ctx, grad_output):
        theta, = ctx.saved_tensors
        grad_output = ApplyRotaryEmbeddingInplace.apply(grad_output.clone(), theta, not ctx.conj)
        return grad_output, None, None

    @staticmethod
    def jvp(ctx, grad_input, _, __):
        theta, = ctx.saved_tensors
        return ApplyRotaryEmbeddingInplace.apply(grad_input, theta, ctx.conj)


def apply_rotary_emb_(x, theta):
    return ApplyRotaryEmbeddingInplace.apply(x, theta, False)


class AdaRMSNorm(nn.Module):
    def __init__(self, features, scale_features = None, eps = 1e-6):
        super().__init__()
        self.eps = eps
        self.scale = apply_wd(zero_init(Linear(scale_features, features, bias=False)))
        tag_module(self.scale, "mapping")

    def extra_repr(self):
        return f"eps={self.eps},"

    def forward(self, input, scale):
        return rms_norm(input, self.scale(scale)[:, None, None, :] + 1, self.eps)


class AutoAdaRMSNorm(nn.Module):
    def __init__(self, features: int, scale_features: Optional[int] = None, eps: float = 1.e-6):
        super().__init__()
        self.eps = eps
        if scale_features is None:
            self.scale = nn.Parameter(torch.ones(features))
            tag_param(self.scale, "mapping")
        else:
            self.scale = apply_wd(zero_init(Linear(scale_features, features, bias=False)))
            tag_module(self.scale, "mapping")

    def extra_repr(self):
        if isinstance(self.scale, nn.Parameter):
            return f"shape={tuple(self.scale.shape)}, eps={self.eps}"
        else:
            return f"eps={self.eps}"

    def forward(self, input, scale = None):
        if scale is None:
            scale = self.scale
        else:
            scale = self.scale(scale)[:, None, None, :] + 1
        return rms_norm(input, scale, self.eps)


class LinearGEGLU(nn.Linear):
    def __init__(self, in_features, out_features, bias = True):
        super().__init__(in_features, out_features * 2, bias=bias)
        self.out_features = out_features

    def forward(self, x):
        flops.op(flops.op_linear, x.shape, self.weight.shape)
        return linear_geglu(x, self.weight, self.bias)


class RMSNorm(nn.Module):
    def __init__(self, shape, eps=1e-6):
        super().__init__()
        self.eps = eps
        self.scale = nn.Parameter(torch.ones(shape))

    def extra_repr(self):
        return f"shape={tuple(self.scale.shape)}, eps={self.eps}"

    def forward(self, input):
        return rms_norm(input, self.scale, self.eps)


class RMSNormIgnored(RMSNorm):
    def forward(self, input, *args):
        return super().forward(input)


class AxialRoPE(nn.Module):
    def __init__(self, dim, n_heads):
        super().__init__()
        log_min = math.log(math.pi)
        log_max = math.log(10.0 * math.pi)
        freqs = torch.linspace(log_min, log_max, n_heads * dim // 4 + 1)[:-1].exp()
        self.register_buffer("freqs", freqs.view(dim // 4, n_heads).T.contiguous())

    def extra_repr(self):
        return f"dim={self.freqs.shape[1] * 4}, n_heads={self.freqs.shape[0]}"

    def forward(self, pos):
        theta_h = pos[..., None, 0:1] * self.freqs.to(pos.dtype)
        theta_w = pos[..., None, 1:2] * self.freqs.to(pos.dtype)
        return torch.cat((theta_h, theta_w), dim=-1)


class FeedForwardBlock(nn.Module):
    def __init__(self, d_model, d_ff, cond_features = None, dropout=0.0):
        super().__init__()
        if cond_features is None:
            self.norm = RMSNormIgnored(d_model)
        else:
            self.norm = AdaRMSNorm(d_model, cond_features)
        self.up_proj = apply_wd(LinearGEGLU(d_model, d_ff, bias=False))
        self.dropout = nn.Dropout(dropout)
        self.down_proj = apply_wd(zero_init(Linear(d_ff, d_model, bias=False)))

    def forward(self, x, cond = None):
        skip = x
        x = self.norm(x, cond)
        x = self.up_proj(x)
        x = self.dropout(x)
        x = self.down_proj(x)
        return x + skip


class Linear(nn.Linear):
    def forward(self, x):
        flops.op(flops.op_linear, x.shape, self.weight.shape)
        return super().forward(x)


# Token merging and splitting
class TokenMerge(nn.Module):
    def __init__(self, in_features, out_features, patch_size=(2, 2)):
        super().__init__()
        self.h = patch_size[0]
        self.w = patch_size[1]
        self.proj = apply_wd(Linear(in_features * self.h * self.w, out_features, bias=False))

    def forward(self, x):
        x = rearrange(x, "... (h nh) (w nw) e -> ... h w (nh nw e)", nh=self.h, nw=self.w)
        return self.proj(x)


class TokenSplitWithoutSkip(nn.Module):
    def __init__(self, in_features, out_features, patch_size=(2, 2)):
        super().__init__()
        self.h = patch_size[0]
        self.w = patch_size[1]
        self.proj = apply_wd(Linear(in_features, out_features * self.h * self.w, bias=False))

    def forward(self, x):
        x = self.proj(x)
        return rearrange(x, "... h w (nh nw e) -> ... (h nh) (w nw) e", nh=self.h, nw=self.w)


class TokenSplit(nn.Module):
    def __init__(self, in_features, out_features, patch_size=(2, 2)):
        super().__init__()
        self.h = patch_size[0]
        self.w = patch_size[1]
        self.proj = apply_wd(Linear(in_features, out_features * self.h * self.w, bias=False))
        self.fac = nn.Parameter(torch.ones(1) * 0.5)
    
    def lerp(self, x, skip):
        return torch.lerp(skip, x, self.fac.to(x.dtype))

    def forward(self, x, skip):
        x = self.proj(x)
        x = rearrange(x, "... h w (nh nw e) -> ... (h nh) (w nw) e", nh=self.h, nw=self.w)
        return self.lerp(x, skip)


class Identity(nn.Identity):
    def forward(self, input, *args, **kwargs):
        return super().forward(input)


def zero_module(module: nn.Module):
    """
    Zero out the parameters of a module and return it.
    """
    for p in module.parameters():
        p.detach().zero_()
    return module


def bmm(a, b):
    return torch.einsum('b...i,bi...o->b...o', a, b)