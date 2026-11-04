"""
Modul Komponen Konvolusi Kompleks (Complex-Valued Convolution & Operations).

Mengimplementasikan:
1. ComplexConv2d: Operasi konvolusi 2D pada domain kompleks:
   (X_r * W_r - X_i * W_i) + j * (X_r * W_i + X_i * W_r)
2. ComplexConvTranspose2d: Operasi konvolusi transposisi 2D kompleks (upsampling).
3. ComplexBatchNorm2d: Normalisasi batch untuk tensor bilangan kompleks.
4. ComplexActivation: Aktivasi non-linier kompleks (ModReLU / Complex LeakyReLU).
5. ComplexResidualBlock: Blok residual dengan injeksi time embedding t.
"""

import math
from typing import Optional, Tuple
import torch
import torch.nn as nn
import torch.nn.functional as F


class ComplexConv2d(nn.Module):
    """
    Konvolusi 2D Kompleks.
    Menerima tensor [B, 2*C_in, H, W] di mana C_in kanal real dan C_in kanal imajiner.
    Menghasilkan tensor [B, 2*C_out, H, W].
    """
    def __init__(
        self,
        in_channels: int,
        out_channels: int,
        kernel_size: Tuple[int, int] = (3, 3),
        stride: Tuple[int, int] = (1, 1),
        padding: Tuple[int, int] = (1, 1),
        bias: bool = True
    ):
        super().__init__()
        self.in_channels = in_channels
        self.out_channels = out_channels

        # Bobot konvolusi bagian real dan imajiner
        self.conv_r = nn.Conv2d(in_channels, out_channels, kernel_size, stride, padding, bias=bias)
        self.conv_i = nn.Conv2d(in_channels, out_channels, kernel_size, stride, padding, bias=bias)

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        # x memiliki bentuk [B, 2, C, H, W] atau [B, 2*C, H, W]
        # Di sini kita asumsikan input berdimensi [B, 2*C_in, H, W] di mana separuh pertama adalah real, separuh kedua adalah imag
        real, imag = torch.chunk(x, 2, dim=1)

        out_r = self.conv_r(real) - self.conv_i(imag)
        out_i = self.conv_r(imag) + self.conv_i(real)

        return torch.cat([out_r, out_i], dim=1)


class ComplexConvTranspose2d(nn.Module):
    """
    Konvolusi Transposisi 2D Kompleks untuk Upsampling pada Decoder U-Net.
    """
    def __init__(
        self,
        in_channels: int,
        out_channels: int,
        kernel_size: Tuple[int, int] = (3, 3),
        stride: Tuple[int, int] = (2, 2),
        padding: Tuple[int, int] = (1, 1),
        output_padding: Tuple[int, int] = (1, 1),
        bias: bool = True
    ):
        super().__init__()
        self.conv_tr_r = nn.ConvTranspose2d(
            in_channels, out_channels, kernel_size, stride, padding, output_padding, bias=bias
        )
        self.conv_tr_i = nn.ConvTranspose2d(
            in_channels, out_channels, kernel_size, stride, padding, output_padding, bias=bias
        )

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        real, imag = torch.chunk(x, 2, dim=1)

        out_r = self.conv_tr_r(real) - self.conv_tr_i(imag)
        out_i = self.conv_tr_r(imag) + self.conv_tr_i(real)

        return torch.cat([out_r, out_i], dim=1)


class ComplexBatchNorm2d(nn.Module):
    """
    Batch Normalization untuk Tensor Kompleks.
    Melakukan normalisasi terpisah pada bagian real dan imajiner.
    """
    def __init__(self, num_features: int, eps: float = 1e-5):
        super().__init__()
        self.bn_r = nn.BatchNorm2d(num_features, eps=eps)
        self.bn_i = nn.BatchNorm2d(num_features, eps=eps)

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        real, imag = torch.chunk(x, 2, dim=1)
        norm_r = self.bn_r(real)
        norm_i = self.bn_i(imag)
        return torch.cat([norm_r, norm_i], dim=1)


class ComplexLeakyReLU(nn.Module):
    """
    Aktivasi LeakyReLU yang diaplikasikan pada komponen real dan imajiner.
    """
    def __init__(self, negative_slope: float = 0.2):
        super().__init__()
        self.act_r = nn.LeakyReLU(negative_slope)
        self.act_i = nn.LeakyReLU(negative_slope)

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        real, imag = torch.chunk(x, 2, dim=1)
        return torch.cat([self.act_r(real), self.act_i(imag)], dim=1)


class SinusoidalPositionalEmbedding(nn.Module):
    """
    Positional Embedding Sinusoidal untuk Langkah Waktu Difusi Kontinu t in [0, 1].
    """
    def __init__(self, dim: int):
        super().__init__()
        self.dim = dim

    def forward(self, t: torch.Tensor) -> torch.Tensor:
        # t: [B]
        half_dim = self.dim // 2
        freqs = torch.exp(
            -math.log(10000.0) * torch.arange(start=0, end=half_dim, dtype=torch.float32, device=t.device) / half_dim
        )
        args = t[:, None].float() * freqs[None, :]
        embedding = torch.cat([torch.cos(args), torch.sin(args)], dim=-1)
        if self.dim % 2 == 1:
            embedding = F.pad(embedding, (0, 1))
        return embedding


class ComplexResidualBlock(nn.Module):
    """
    Residual Block Kompleks dengan Pengkondisian Time Step Embedding t.
    """
    def __init__(
        self,
        in_channels: int,
        out_channels: int,
        time_embed_dim: int,
        dropout: float = 0.1
    ):
        super().__init__()
        self.in_channels = in_channels
        self.out_channels = out_channels

        self.conv1 = ComplexConv2d(in_channels, out_channels, kernel_size=(3, 3), padding=(1, 1))
        self.norm1 = ComplexBatchNorm2d(out_channels)
        self.act1 = ComplexLeakyReLU(0.2)

        self.time_proj = nn.Linear(time_embed_dim, out_channels * 2)

        self.conv2 = ComplexConv2d(out_channels, out_channels, kernel_size=(3, 3), padding=(1, 1))
        self.norm2 = ComplexBatchNorm2d(out_channels)
        self.act2 = ComplexLeakyReLU(0.2)
        self.dropout = nn.Dropout(dropout)

        if in_channels != out_channels:
            self.shortcut = ComplexConv2d(in_channels, out_channels, kernel_size=(1, 1), padding=(0, 0))
        else:
            self.shortcut = nn.Identity()

    def forward(self, x: torch.Tensor, time_embed: torch.Tensor) -> torch.Tensor:
        # x: [B, 2 * in_channels, H, W]
        # time_embed: [B, time_embed_dim]
        h = self.conv1(x)
        h = self.norm1(h)
        h = self.act1(h)

        # Proyeksikan time embedding dan tambahkan ke h
        time_bias = self.time_proj(time_embed)[:, :, None, None]  # [B, 2*out_channels, 1, 1]
        h = h + time_bias

        h = self.conv2(h)
        h = self.norm2(h)
        h = self.dropout(h)

        res = self.shortcut(x)
        return self.act2(h + res)
