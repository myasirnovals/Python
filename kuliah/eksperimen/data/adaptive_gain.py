"""
Modul Adaptive Gain Normalization untuk Sinyal Wicara Anak Cleft Lip and Palate.

Sesuai dengan Persamaan (4) pada Proposal Penelitian:
    g = min( 10^((Target_dBFS - Peak_dBFS) / 20), G_max )
    x_norm(t) = g * x(t)

Modul ini menormalkan rentang dinamis audio UltraSuite yang memiliki
headroom amplitudo sangat rendah (-38 hingga -48 dBFS) ke taraf standar
-23 dBFS (EBU R128) tanpa memicu pemotongan sinyal (clipping saturation).
"""

import math
from typing import Tuple, Union
import numpy as np


class AdaptiveGainNormalizer:
    """
    Normalisasi Penguatan Adaptif Dinamis untuk Audio Wicara Klinis.
    
    Attributes:
        target_dbfs (float): Ambang target level puncak dalam dBFS (default: -23.0 dBFS).
        max_gain (float): Faktor penguatan maksimum yang diizinkan (default: 90.0).
        eps (float): Nilai stabilitas numerik untuk mencegah log(0).
    """

    def __init__(self, target_dbfs: float = -23.0, max_gain: float = 90.0, eps: float = 1e-9):
        self.target_dbfs = float(target_dbfs)
        self.max_gain = float(max_gain)
        self.eps = float(eps)

    def compute_peak_dbfs(self, audio: np.ndarray) -> float:
        """Menghitung level puncak absolut sinyal audio dalam satuan dBFS."""
        peak_val = np.max(np.abs(audio))
        if peak_val < self.eps:
            return -100.0  # Mendekati keheningan mutlak
        return 20.0 * math.log10(peak_val)

    def compute_robust_peak_dbfs(self, audio: np.ndarray, percentile: float = 99.5) -> float:
        """
        Menghitung level puncak robust (persentil) untuk mengabaikan
        letupan sesaat mikrofon (transient clicks/pops) atau tarikan napas tunggal.
        """
        abs_audio = np.abs(audio)
        if len(abs_audio) == 0 or np.max(abs_audio) < self.eps:
            return -100.0
        robust_peak = float(np.percentile(abs_audio, percentile))
        if robust_peak < self.eps:
            robust_peak = float(np.max(abs_audio))
        return 20.0 * math.log10(max(robust_peak, self.eps))

    def compute_rms_dbfs(self, audio: np.ndarray, silence_threshold_db: float = -50.0) -> float:
        """
        Menghitung level energi wicara aktif (Active Speech RMS) dalam satuan dBFS.
        Mengabaikan frame hening di awal dan akhir rekaman.
        """
        abs_audio = np.abs(audio)
        if len(abs_audio) == 0 or np.max(abs_audio) < self.eps:
            return -100.0

        frame_size = 512
        hop = 256
        if len(audio) < frame_size:
            rms_val = np.sqrt(np.mean(np.square(audio)))
            return 20.0 * math.log10(max(rms_val, self.eps))

        frames = [audio[i:i + frame_size] for i in range(0, len(audio) - frame_size, hop)]
        frame_rms = np.array([np.sqrt(np.mean(np.square(f))) for f in frames])
        
        # Ambang deteksi wicara aktif (default: -50 dBFS = 10^(-50/20) ~ 0.00316)
        threshold = 10.0 ** (silence_threshold_db / 20.0)
        active_frames = frame_rms[frame_rms > threshold]
        
        if len(active_frames) == 0:
            rms_val = np.sqrt(np.mean(np.square(audio)))
        else:
            rms_val = np.mean(active_frames)

        return 20.0 * math.log10(max(rms_val, self.eps))

    def compute_gain_factor(self, audio: np.ndarray, mode: str = "rms") -> float:
        """
        Menghitung faktor penguatan adaptif g.
        
        Sesuai Persamaan (4) Proposal:
            g = min( 10^((Target_dBFS - Level_dBFS) / 20), G_max )
        
        Perbaikan:
        - Menggunakan Active Speech RMS (standar EBU R128) untuk merepresentasikan
          kenyaringan sebenarnya dari anak CLP.
        - Jika rekaman sudah bersuara normal / jelas (Level >= Target), gain
          dipertahankan pada taraf aman ~1.0x (tidak meredam audio yang sudah jelas).
        - Menghindari pemotongan sinyal (clipping) dengan batas aman puncak 0.95.
        """
        if mode == "rms":
            level_dbfs = self.compute_rms_dbfs(audio)
        else:
            level_dbfs = self.compute_robust_peak_dbfs(audio)

        if level_dbfs <= -100.0:
            return 1.0  # Sinyal hening mutlak tidak diperkuat

        diff_db = self.target_dbfs - level_dbfs
        ideal_gain = 10.0 ** (diff_db / 20.0)

        raw_peak = np.max(np.abs(audio))

        # Jika wicara sudah berada pada atau di atas target (-23 dBFS):
        # Jangan redam sinyal normal, pertahankan level asli (1.0x) kecuali raw_peak rawan clipping
        if diff_db <= 0:
            ideal_gain = min(1.0, 0.95 / max(raw_peak, self.eps))

        # Batas penguatan aman untuk mencegah clipping pada lonjakan sesaat
        if raw_peak > self.eps:
            max_safe_gain = 0.95 / raw_peak
            ideal_gain = min(ideal_gain, max_safe_gain)

        gain = float(min(max(ideal_gain, 0.5), self.max_gain))
        return gain

    def normalize(self, audio: np.ndarray, mode: str = "rms") -> Tuple[np.ndarray, float]:
        """
        Menerapkan normalisasi gain adaptif pada sinyal audio.

        Args:
            audio (np.ndarray): Sinyal wicara mono (1D float array [-1.0, 1.0]).
            mode (str): 'rms' (default, EBU R128 active speech) atau 'peak'.

        Returns:
            Tuple[np.ndarray, float]: (audio_ternormalisasi, faktor_penguatan_g)
        """
        g = self.compute_gain_factor(audio, mode=mode)
        normalized = audio * g

        # Proteksi hard clipping jika terjadi overshoot sesaat
        max_abs = np.max(np.abs(normalized))
        if max_abs > 0.999:
            normalized = (normalized / max_abs) * 0.999

        return normalized.astype(np.float32), g

    def denormalize(self, audio: np.ndarray, gain_factor: float) -> np.ndarray:
        """
        Membalikkan normalisasi gain adaptif ke taraf energi asli jika diperlukan.

        Args:
            audio (np.ndarray): Sinyal wicara hasil restorasi model.
            gain_factor (float): Faktor penguatan g yang dipakai saat pra-proses.

        Returns:
            np.ndarray: Sinyal terestorasi pada skala energi semula.
        """
        if gain_factor <= self.eps:
            return audio
        return (audio / gain_factor).astype(np.float32)


# Verifikasi fungsionalitas modul jika dijalankan langsung
if __name__ == "__main__":
    normalizer = AdaptiveGainNormalizer(target_dbfs=-23.0, max_gain=90.0)
    
    # Simulasi rekaman hening khas UltraSuite (-42 dBFS)
    t = np.linspace(0, 1.0, 22050)
    simulated_speech = 0.008 * np.sin(2 * np.pi * 440 * t)  # ~ -41.9 dBFS
    
    peak_before = normalizer.compute_peak_dbfs(simulated_speech)
    norm_audio, g = normalizer.normalize(simulated_speech)
    peak_after = normalizer.compute_peak_dbfs(norm_audio)
    
    print("=== Uji Coba Adaptive Gain Normalizer ===")
    rms_before = normalizer.compute_rms_dbfs(simulated_speech)
    peak_before = normalizer.compute_peak_dbfs(simulated_speech)
    norm_audio, g = normalizer.normalize(simulated_speech, mode="rms")
    rms_after = normalizer.compute_rms_dbfs(norm_audio)
    peak_after = normalizer.compute_peak_dbfs(norm_audio)

    print(f"RMS Sebelum Normalisasi  : {rms_before:.2f} dBFS")
    print(f"Peak Sebelum Normalisasi : {peak_before:.2f} dBFS")
    print(f"Faktor Penguatan (g)     : {g:.2f}x")
    print(f"RMS Setelah Normalisasi  : {rms_after:.2f} dBFS (Target: -23.0 dBFS)")
    print(f"Peak Setelah Normalisasi : {peak_after:.2f} dBFS")
    assert abs(rms_after - (-23.0)) < 0.2, "Normalisasi gagal mencapai target RMS dBFS!"
    print("[SUCCESS] Modul normalisasi adaptif bekerja sempurna.")
