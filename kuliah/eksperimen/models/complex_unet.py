"""
Arsitektur Complex-Valued U-Net untuk Penaksiran Skor Gradien Difusi Audio (Score Predictor).

Jaringan ini memetakan masukan:
    - X_t: Spektrogram bernoise pada waktu t [B, 2, F, T] (Real & Imag)
    - Y: Spektrogram kondisi wicara CLP ternormalisasi [B, 2, F, T] (Real & Imag)
    - t: Langkah waktu kontinu difusi [B] in [0, 1]

Menghasilkan:
    - s_theta(X_t, Y, t): Taksiran fungsi skor gradien [B, 2, F, T]
"""

from typing import List, Tuple
import torch
import torch.nn as nn
import torch.nn.functional as F

from .complex_modules import (
    ComplexConv2d,
    ComplexConvTranspose2d,
    ComplexResidualBlock,
    SinusoidalPositionalEmbedding,
    ComplexLeakyReLU
)


class ComplexUNet(nn.Module):
    """
    Complex-Valued U-Net Multi-Skala dengan Pengkondisian Spektrogram CLP dan Time Embedding.
    """
    def __init__(
        self,
        in_channels: int = 2,        # X_t (Real, Imag) = 1 kanal kompleks (2 float)
        cond_channels: int = 2,      # Y (Real, Imag) = 1 kanal kompleks (2 float)
        out_channels: int = 2,       # Skor gradien (Real, Imag) = 1 kanal kompleks (2 float)
        base_channels: int = 32,
        channel_mult: List[int] = [1, 2, 4],
        num_res_blocks: int = 2,
        time_embed_dim: int = 128,
        dropout: float = 0.1,
        beta_min: float = 0.1,
        beta_max: float = 20.0,
        scale_by_sigma: bool = True
    ):
        super().__init__()
        self.in_channels = in_channels
        self.cond_channels = cond_channels
        self.out_channels = out_channels
        self.base_channels = base_channels
        self.channel_mult = channel_mult
        self.time_embed_dim = time_embed_dim
        self.beta_min = float(beta_min)
        self.beta_max = float(beta_max)
        self.scale_by_sigma = scale_by_sigma

        # 1. Modul Embedding Langkah Waktu Kontinu t
        self.time_embed_mlp = nn.Sequential(
            SinusoidalPositionalEmbedding(time_embed_dim),
            nn.Linear(time_embed_dim, time_embed_dim),
            nn.SiLU(),
            nn.Linear(time_embed_dim, time_embed_dim)
        )

        # 2. Proyeksi Masukan Awal: Concatenate X_t dan Y -> Total 2 kanal kompleks (4 float)
        total_in_c = (in_channels + cond_channels) // 2  # 2 kanal kompleks
        self.init_conv = ComplexConv2d(
            in_channels=total_in_c,
            out_channels=base_channels,
            kernel_size=(3, 3),
            padding=(1, 1)
        )

        # 3. Jalur Encoder (Downsampling)
        self.enc_blocks = nn.ModuleList()
        self.down_samples = nn.ModuleList()

        curr_c = base_channels
        for level, mult in enumerate(channel_mult):
            out_c = base_channels * mult
            level_blocks = nn.ModuleList()
            for _ in range(num_res_blocks):
                level_blocks.append(
                    ComplexResidualBlock(curr_c, out_c, time_embed_dim, dropout)
                )
                curr_c = out_c
            self.enc_blocks.append(level_blocks)

            if level != len(channel_mult) - 1:
                # Downsampling dengan stride 2
                self.down_samples.append(
                    ComplexConv2d(curr_c, curr_c, kernel_size=(3, 3), stride=(2, 2), padding=(1, 1))
                )
            else:
                self.down_samples.append(nn.Identity())

        # 4. Bottleneck / Mid Blocks
        self.mid_block1 = ComplexResidualBlock(curr_c, curr_c, time_embed_dim, dropout)
        self.mid_block2 = ComplexResidualBlock(curr_c, curr_c, time_embed_dim, dropout)

        # 5. Jalur Decoder (Upsampling dengan Skip Connection)
        self.dec_blocks = nn.ModuleList()
        self.up_samples = nn.ModuleList()

        for level, mult in reversed(list(enumerate(channel_mult))):
            out_c = base_channels * mult
            level_blocks = nn.ModuleList()
            for b_idx in range(num_res_blocks):
                # Blok pertama level decoder: curr_c (dari level sebelumnya/bottleneck) + out_c (skip connection)
                # Blok berikutnya dalam level yang sama: out_c + out_c (skip connection)
                in_c = (curr_c + out_c) if b_idx == 0 else (out_c + out_c)
                level_blocks.append(
                    ComplexResidualBlock(in_c, out_c, time_embed_dim, dropout)
                )
                curr_c = out_c
            self.dec_blocks.append(level_blocks)

            if level != 0:
                # Upsampling dengan transpose convolution
                self.up_samples.append(
                    ComplexConvTranspose2d(curr_c, curr_c, kernel_size=(3, 3), stride=(2, 2), padding=(1, 1), output_padding=(1, 1))
                )
            else:
                self.up_samples.append(nn.Identity())

        # 6. Proyeksi Akhir: curr_c kompleks -> 1 kanal kompleks (2 float real/imag)
        self.final_act = ComplexLeakyReLU(0.2)
        self.final_conv = ComplexConv2d(
            in_channels=curr_c,
            out_channels=out_channels // 2,  # 1 kanal kompleks
            kernel_size=(3, 3),
            padding=(1, 1)
        )

    def forward(self, x_t: torch.Tensor, y: torch.Tensor, t: torch.Tensor) -> torch.Tensor:
        """
        Args:
            x_t (torch.Tensor): Spektrogram bernoise [B, 2, F, T]
            y (torch.Tensor): Spektrogram kondisi [B, 2, F, T]
            t (torch.Tensor): Langkah waktu difusi kontinu [B] in [0, 1]

        Returns:
            torch.Tensor: Prediksi skor gradien [B, 2, F, T]
        """
        # 1. Embedding Waktu Kontinu t
        time_embed = self.time_embed_mlp(t)  # [B, time_embed_dim]

        # 2. Gabungkan x_t dan y di kanal real dan imag
        # Bentuk: [B, 4, F, T] -> [B, 2, F, T] real dan [B, 2, F, T] imag -> concat di dim 1: [B, 4, F, T]
        x_r = torch.cat([x_t[:, 0:1, :, :], y[:, 0:1, :, :]], dim=1)  # 2 kanal real
        x_i = torch.cat([x_t[:, 1:2, :, :], y[:, 1:2, :, :]], dim=1)  # 2 kanal imag
        h = torch.cat([x_r, x_i], dim=1)  # [B, 4, F, T]

        # Simpan dimensi asli untuk penyesuaian padding pada saat upsampling
        orig_h, orig_w = h.shape[2], h.shape[3]

        h = self.init_conv(h)

        # 3. Encoder Forward & Simpan Skip Connections
        skips = []
        for level, level_blocks in enumerate(self.enc_blocks):
            for block in level_blocks:
                h = block(h, time_embed)
                skips.append(h)
            h = self.down_samples[level](h)

        # 4. Bottleneck Forward
        h = self.mid_block1(h, time_embed)
        h = self.mid_block2(h, time_embed)

        # 5. Decoder Forward dengan Skip Connection
        for level, level_blocks in enumerate(self.dec_blocks):
            for block in level_blocks:
                skip = skips.pop()
                # Interpolasi jika ada perbedaan dimensi 1 piksel karena pembagian ganjil
                if h.shape[2:] != skip.shape[2:]:
                    # Pisahkan real dan imag sebelum interpolate
                    real_h, imag_h = torch.chunk(h, 2, dim=1)
                    real_h = F.interpolate(real_h, size=skip.shape[2:], mode="bilinear", align_corners=False)
                    imag_h = F.interpolate(imag_h, size=skip.shape[2:], mode="bilinear", align_corners=False)
                    h = torch.cat([real_h, imag_h], dim=1)
                
                # Concatenate skip connection di ruang real dan imag
                real_h, imag_h = torch.chunk(h, 2, dim=1)
                real_skip, imag_skip = torch.chunk(skip, 2, dim=1)
                h = torch.cat([real_h, real_skip, imag_h, imag_skip], dim=1)
                h = block(h, time_embed)
            
            h = self.up_samples[level](h)

        # Pastikan output sesuai ukuran asli F x T
        if h.shape[2:] != (orig_h, orig_w):
            real_h, imag_h = torch.chunk(h, 2, dim=1)
            real_h = F.interpolate(real_h, size=(orig_h, orig_w), mode="bilinear", align_corners=False)
            imag_h = F.interpolate(imag_h, size=(orig_h, orig_w), mode="bilinear", align_corners=False)
            h = torch.cat([real_h, imag_h], dim=1)

        # 6. Proyeksi Akhir
        h = self.final_act(h)
        f_theta = self.final_conv(h)  # [B, 2, F, T], unit-scale residual (-noise estimator)

        if self.scale_by_sigma:
            # Penskalaan skor analitis: s_theta = F_theta / sigma(t)
            # Menghilangkan singularitas saat pelatihan dan menstabilkan reverse sampling
            # Sesuai teori Song et al. (2020) & SGMSE+ (Richter et al., 2023)
            log_alpha = -0.25 * (t ** 2) * (self.beta_max - self.beta_min) - 0.5 * t * self.beta_min
            alpha_t = torch.exp(log_alpha)[:, None, None, None]
            sigma_t = torch.sqrt(torch.clamp(1.0 - alpha_t ** 2, min=1e-5))
            score = f_theta / sigma_t
            return score
        else:
            return f_theta
