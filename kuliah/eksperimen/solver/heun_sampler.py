"""
Penyelesai Numerik Difusi Waktu Terbalik (Reverse SDE & Probability Flow ODE Solver).

Mengimplementasikan metode Heun 2nd-Order Predictor-Corrector (Heun Few-Step Sampler):
- Standar default: Deterministic Probability Flow ODE (bebas derau acak liar, menghasilkan audio jernih dan mulus).
- Opsional: Stochastic Reverse SDE jika diinginkan eksperimen stokastik.
- Langkah sampling efisien: N = 30 langkah dari t = 1.0 ke t = eps.
- Tweedie projection pada langkah akhir untuk memperoleh estimasi X_hat_0 bebas derau residu.
"""

from typing import Optional, Callable
import torch
import torch.nn as nn
from tqdm import tqdm

from models.sde import VPSDE


class HeunSampler:
    """
    Penyelesai Numerik Heun Orde 2 untuk Reverse VP-SDE dan Probability Flow ODE.
    """
    def __init__(
        self,
        sde: VPSDE,
        num_steps: int = 30,
        corrector_steps: int = 0,
        snr: float = 0.16,
        eps: float = 1e-3,
        use_ode: bool = True
    ):
        self.sde = sde
        self.num_steps = num_steps
        self.corrector_steps = corrector_steps
        self.snr = snr
        self.eps = eps
        self.use_ode = use_ode

    @torch.no_grad()
    def sample(
        self,
        score_model: nn.Module,
        condition_y: torch.Tensor,
        show_progress: bool = True
    ) -> torch.Tensor:
        """
        Melakukan inferensi difusi terbalik dari derau ke spektrogram wicara bersih.

        Args:
            score_model (nn.Module): Model Complex U-Net terlatih.
            condition_y (torch.Tensor): Spektrogram kondisi CLP ternormalisasi [B, 2, F, T].
            show_progress (bool): Tampilkan progress bar sampling.

        Returns:
            torch.Tensor: Spektrogram bersih terestorasi X_hat_0 [B, 2, F, T].
        """
        score_model.eval()
        device = condition_y.device
        batch_size, channels, freq_bins, time_frames = condition_y.shape

        # 1. Inisialisasi dari Derau Gaussian Murni pada t = 1.0
        x = torch.randn(batch_size, channels, freq_bins, time_frames, device=device)

        # Diskritisasi waktu dari 1.0 ke eps secara linier
        timesteps = torch.linspace(1.0, self.eps, self.num_steps + 1, device=device)

        sampler_type = "ODE" if self.use_ode else "SDE"
        pbar = tqdm(range(self.num_steps), desc=f"[{sampler_type} Heun Sampling]", disable=not show_progress)
        for i in pbar:
            t_curr = timesteps[i]
            t_next = timesteps[i + 1]
            dt = t_next - t_curr  # dt bernilai negatif karena berjalan mundur

            t_batch_curr = torch.full((batch_size,), t_curr, device=device)
            t_batch_next = torch.full((batch_size,), t_next, device=device)

            if self.use_ode:
                # --- PROBABILITY FLOW ODE HEUN METHOD (DETERMINISTIK & JERNIH) ---
                # dx / dt = -1/2 * beta(t) * (x + score)
                # Tahap 1: Prediktor Euler
                score_curr = score_model(x, condition_y, t_batch_curr)
                d_curr = self.sde.reverse_ode_drift(x, score_curr, t_batch_curr)
                x_pred = x + dt * d_curr

                # Tahap 2: Korektor Trapezoidal / Heun (RK2)
                score_next = score_model(x_pred, condition_y, t_batch_next)
                d_next = self.sde.reverse_ode_drift(x_pred, score_next, t_batch_next)

                d_avg = 0.5 * (d_curr + d_next)
                x = x + dt * d_avg
            else:
                # --- STOCHASTIC REVERSE SDE HEUN METHOD ---
                score_curr = score_model(x, condition_y, t_batch_curr)
                drift_curr = self.sde.reverse_drift(x, score_curr, t_batch_curr)
                diff_curr = self.sde.diffusion(t_batch_curr)[:, None, None, None]

                dw = torch.randn_like(x) * torch.sqrt(torch.abs(dt))
                x_pred = x + drift_curr * dt + diff_curr * dw

                score_next = score_model(x_pred, condition_y, t_batch_next)
                drift_next = self.sde.reverse_drift(x_pred, score_next, t_batch_next)
                diff_next = self.sde.diffusion(t_batch_next)[:, None, None, None]

                drift_avg = 0.5 * (drift_curr + drift_next)
                diff_avg = 0.5 * (diff_curr + diff_next)
                x = x + drift_avg * dt + diff_avg * dw

                # Korektor Langevin hanya dijalankan jika corrector_steps > 0 dan t masih tinggi
                if self.corrector_steps > 0 and t_next > 0.05:
                    for _ in range(self.corrector_steps):
                        score_c = score_model(x, condition_y, t_batch_next)
                        norm_score = torch.norm(score_c.reshape(batch_size, -1), dim=-1, keepdim=True)[:, :, None, None]
                        step_size = 2.0 * ((self.snr * t_next) / (norm_score + 1e-8)) ** 2
                        z = torch.randn_like(x)
                        x = x + step_size * score_c + torch.sqrt(2.0 * step_size) * z

        # Tweedie's formula pada langkah akhir t = eps untuk memproyeksikan ke X_0 analitis murni
        t_final = torch.full((batch_size,), self.eps, device=device)
        final_score = score_model(x, condition_y, t_final)
        var_final = self.sde.var(t_final)[:, None, None, None]
        alpha_final = self.sde.mean_coeff(t_final)[:, None, None, None]

        x_clean = (x + var_final * final_score) / torch.clamp(alpha_final, min=1e-5)
        return x_clean
