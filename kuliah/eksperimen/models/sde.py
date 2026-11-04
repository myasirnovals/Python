"""
Formulasi Persamaan Diferensial Stokastik Waktu Kontinu (Continuous-Time SDE).

Mengimplementasikan Variance-Preserving SDE (VP-SDE):
    dX_t = -1/2 * beta(t) * X_t dt + sqrt(beta(t)) * dw_t

Dengan parameter analitis:
    beta(t) = beta_min + t * (beta_max - beta_min), t in [0, 1]
    alpha(t) = exp( -1/4 * t^2 * (beta_max - beta_min) - 1/2 * t * beta_min )
    sigma(t)^2 = 1 - alpha(t)^2
    p_0t(X_t | X_0) = N_C( X_t; alpha(t) * X_0, sigma(t)^2 * I )
"""

import math
from typing import Tuple
import torch
import torch.nn as nn


class VPSDE(nn.Module):
    """
    Continuous-Time Variance-Preserving SDE untuk Restorasi Sinyal Wicara.
    """
    def __init__(self, beta_min: float = 0.1, beta_max: float = 20.0, eps: float = 1e-5):
        super().__init__()
        self.beta_min = float(beta_min)
        self.beta_max = float(beta_max)
        self.eps = float(eps)

    def beta(self, t: torch.Tensor) -> torch.Tensor:
        """Jadwal derau linier beta(t) pada t in [0, 1]."""
        return self.beta_min + t * (self.beta_max - self.beta_min)

    def mean_coeff(self, t: torch.Tensor) -> torch.Tensor:
        """Koefisien rata-rata marginal alpha(t)."""
        log_alpha = -0.25 * (t ** 2) * (self.beta_max - self.beta_min) - 0.5 * t * self.beta_min
        return torch.exp(log_alpha)

    def var(self, t: torch.Tensor) -> torch.Tensor:
        """Variansi marginal sigma(t)^2 = 1 - alpha(t)^2."""
        alpha = self.mean_coeff(t)
        return 1.0 - (alpha ** 2)

    def std(self, t: torch.Tensor) -> torch.Tensor:
        """Standar deviasi marginal sigma(t)."""
        return torch.sqrt(torch.clamp(self.var(t), min=self.eps))

    def sample_marginal(self, x_0: torch.Tensor, t: torch.Tensor) -> Tuple[torch.Tensor, torch.Tensor, torch.Tensor]:
        """
        Menginjeksi derau Gaussian standar ke spektrogram bersih X_0 pada waktu t.

        Args:
            x_0 (torch.Tensor): Spektrogram bersih [B, 2, F, T] (Real & Imag).
            t (torch.Tensor): Langkah waktu difusi [B].

        Returns:
            Tuple[torch.Tensor, torch.Tensor, torch.Tensor]:
                - x_t: Spektrogram bernoise [B, 2, F, T]
                - noise: Derau Gaussian standar yang diinjeksikan [B, 2, F, T]
                - score_gt: Skor analitis ground truth [B, 2, F, T]
        """
        # Dimensi broadcast untuk t
        alpha_t = self.mean_coeff(t)[:, None, None, None]  # [B, 1, 1, 1]
        sigma_t = self.std(t)[:, None, None, None]         # [B, 1, 1, 1]
        var_t = self.var(t)[:, None, None, None]           # [B, 1, 1, 1]

        # Sampel derau Gaussian standar bernilai real untuk kedua kanal (real dan imag)
        noise = torch.randn_like(x_0)

        # Perturbation Kernel: X_t = alpha(t) * X_0 + sigma(t) * noise
        x_t = alpha_t * x_0 + sigma_t * noise

        # Skor Analitis Ground Truth: nabla_{X_t} log p_{0t}(X_t | X_0) = - (X_t - alpha_t * X_0) / var_t = - noise / sigma_t
        score_gt = -noise / torch.clamp(sigma_t, min=self.eps)

        return x_t, noise, score_gt

    def reverse_drift(self, x_t: torch.Tensor, score: torch.Tensor, t: torch.Tensor) -> torch.Tensor:
        """
        Menghitung drift term untuk persamaan diferensial terbalik (Reverse SDE):
        f_rev(X_t, t) = -1/2 * beta(t) * X_t - beta(t) * score
        """
        beta_t = self.beta(t)[:, None, None, None]
        return -0.5 * beta_t * x_t - beta_t * score

    def reverse_ode_drift(self, x_t: torch.Tensor, score: torch.Tensor, t: torch.Tensor) -> torch.Tensor:
        """
        Menghitung drift term untuk Probability Flow ODE (Reverse ODE):
        dx / dt = -1/2 * beta(t) * x_t - 1/2 * beta(t) * score
                = -1/2 * beta(t) * (x_t + score)
        Deterministik, bebas dari injeksi derau Brownian terbalik dw_t.
        """
        beta_t = self.beta(t)[:, None, None, None]
        return -0.5 * beta_t * (x_t + score)

    def diffusion(self, t: torch.Tensor) -> torch.Tensor:
        """Koefisien difusi g(t) = sqrt(beta(t))."""
        return torch.sqrt(self.beta(t))
