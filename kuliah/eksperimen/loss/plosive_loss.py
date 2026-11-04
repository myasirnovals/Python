"""
Modul Fungsi Kerugian Hibrida Berbobot Plosif (Plosive-Weighted Hybrid Loss).

Sesuai dengan Persamaan (5), (6), dan (7) pada Proposal Penelitian:
    L_total(theta) = L_score(theta) + gamma * L_plosive(theta)

Di mana:
1. L_score: Meminimalkan galat estimasi skor gradien difusi SDE (score matching berbobot sigma_t^2):
   L_score = E[ sigma(t)^2 * || s_theta(X_t, Y, t) - nabla_{X_t} log p_{0t}(X_t | X_0) ||_2^2 ]
           = E[ || sigma(t) * s_theta(X_t, Y, t) + noise ||_2^2 ]

2. L_plosive: Memberikan penalti bobot ekstra pada pita frekuensi konsonan letup oral plosif
   (/p/, /t/, /k/ pada rentang 1.500 Hz s/d 8.000 Hz) menggunakan rekonstruksi analitis Tweedie:
   X_hat_0 = ( X_t + sigma(t)^2 * s_theta ) / alpha(t)
   L_plosive = || M_plosive * (X_0 - X_hat_0) ||_2^2
"""

from typing import Tuple, Dict
import torch
import torch.nn as nn
import torch.nn.functional as F

from models.sde import VPSDE


class PlosiveWeightedHybridLoss(nn.Module):
    """
    Fungsi Kerugian Hibrida dengan Pembobotan Khusus pada Komponen Plosif Cleft Palate.
    """
    def __init__(
        self,
        sde: VPSDE,
        gamma_plosive: float = 0.25,
        sample_rate: int = 22050,
        n_fft: int = 512,
        plosive_freq_min_hz: float = 1500.0,
        plosive_freq_max_hz: float = 8000.0,
        plosive_boost_factor: float = 3.0
    ):
        super().__init__()
        self.sde = sde
        self.gamma_plosive = float(gamma_plosive)
        self.sample_rate = sample_rate
        self.n_fft = n_fft
        self.plosive_freq_min_hz = plosive_freq_min_hz
        self.plosive_freq_max_hz = plosive_freq_max_hz
        self.plosive_boost_factor = plosive_boost_factor

        # Buat Masker Frekuensi Plosif M_plosive: [1, 1, F, 1]
        num_bins = n_fft // 2 + 1  # 257 bin
        freq_resolution = (sample_rate / 2.0) / (num_bins - 1)  # ~43.06 Hz per bin

        mask = torch.ones(1, 1, num_bins, 1, dtype=torch.float32)
        min_bin = int(plosive_freq_min_hz / freq_resolution)
        max_bin = min(int(plosive_freq_max_hz / freq_resolution), num_bins - 1)

        # Berikan faktor pembobotan lebih tinggi pada pita konsonan plosif
        mask[:, :, min_bin:max_bin + 1, :] = plosive_boost_factor
        self.register_buffer("plosive_mask", mask)

    def forward(
        self,
        score_pred: torch.Tensor,
        x_0: torch.Tensor,
        x_t: torch.Tensor,
        noise: torch.Tensor,
        t: torch.Tensor
    ) -> Dict[str, torch.Tensor]:
        """
        Menghitung total kerugian hibrida.

        Args:
            score_pred (torch.Tensor): Taksiran skor s_theta [B, 2, F, T]
            x_0 (torch.Tensor): Spektrogram bersih target [B, 2, F, T]
            x_t (torch.Tensor): Spektrogram bernoise [B, 2, F, T]
            noise (torch.Tensor): Derau Gaussian standar yang diinjeksikan [B, 2, F, T]
            t (torch.Tensor): Langkah waktu difusi [B] in [0, 1]

        Returns:
            Dict[str, torch.Tensor]: Dictionary berisi 'loss_total', 'loss_score', dan 'loss_plosive'.
        """
        sigma_t = self.sde.std(t)[:, None, None, None]     # [B, 1, 1, 1]
        var_t = self.sde.var(t)[:, None, None, None]       # [B, 1, 1, 1]
        alpha_t = self.sde.mean_coeff(t)[:, None, None, None]  # [B, 1, 1, 1]

        # 1. Score Matching Loss (L_score)
        # Sesuai teori SGMSE+: L_score = E[ || sigma_t * s_theta + noise ||^2 ]
        score_err = sigma_t * score_pred + noise
        loss_score = torch.mean(score_err ** 2)

        # 2. Tweedie's Denoising Reconstruction dengan Time-Weighting alpha_t^2
        # Mengalikan selisih Tweedie dengan alpha_t:
        # alpha_t * (X_0 - X_hat_0) = alpha_t * X_0 - (X_t + var_t * score_pred)
        # Formulasi ini secara matematis mengeliminasi pembagian 1/alpha_t saat t mendekati 1,
        # menjaga stabilitas magnitudo loss pada skala yang seimbang dengan L_score
        diff_scaled = alpha_t * x_0 - (x_t + var_t * score_pred)

        # 3. Plosive-Weighted Loss (L_plosive)
        # Menghitung selisih spektral dengan masker pita frekuensi plosif
        weighted_rec_err = diff_scaled * self.plosive_mask.to(x_0.device)
        loss_plosive = torch.mean(weighted_rec_err ** 2)

        # 4. Total Loss
        total_loss = loss_score + self.gamma_plosive * loss_plosive

        return {
            "loss_total": total_loss,
            "loss_score": loss_score,
            "loss_plosive": loss_plosive
        }
