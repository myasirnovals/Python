"""
Modul Evaluasi Kualitas Akustik Objektif (PESQ & ESTOI).

Mengimplementasikan:
1. PESQ (Perceptual Evaluation of Speech Quality, ITU-T P.862 / P.862.2, skala -0.5 s/d 4.5).
2. ESTOI (Extended Short-Time Objective Intelligibility, skala 0.0 s/d 1.0).
3. SI-SDR (Scale-Invariant Signal-to-Distortion Ratio).
"""

from typing import Dict, Optional
import numpy as np


def compute_metrics(
    clean_audio: np.ndarray,
    restored_audio: np.ndarray,
    sample_rate: int = 22050
) -> Dict[str, float]:
    """
    Menghitung skor metrik objektif PESQ dan ESTOI antara sinyal referensi dan hasil restorasi.

    Args:
        clean_audio (np.ndarray): Sinyal wicara referensi / target (1D float).
        restored_audio (np.ndarray): Sinyal wicara hasil restorasi model (1D float).
        sample_rate (int): Frekuensi cuplikan sinyal.

    Returns:
        Dict[str, float]: Nilai 'pesq_wb', 'estoi', dan 'si_sdr'.
    """
    # Samakan panjang array
    min_len = min(len(clean_audio), len(restored_audio))
    clean = clean_audio[:min_len].astype(np.float32)
    restored = restored_audio[:min_len].astype(np.float32)

    results = {}

    # 1. ESTOI (Extended STOI)
    try:
        from pystoi import stoi
        estoi_val = stoi(clean, restored, sample_rate, extended=True)
        results["estoi"] = float(estoi_val)
    except Exception as e:
        results["estoi"] = float("nan")

    # 2. PESQ (Wideband / Narrowband)
    try:
        from pesq import pesq
        # PESQ memerlukan sample rate 16000 atau 8000
        if sample_rate != 16000:
            import scipy.signal
            num_samples_16k = int(min_len * 16000 / sample_rate)
            clean_16k = scipy.signal.resample(clean, num_samples_16k)
            rest_16k = scipy.signal.resample(restored, num_samples_16k)
            pesq_wb = pesq(16000, clean_16k, rest_16k, "wb")
        else:
            pesq_wb = pesq(16000, clean, restored, "wb")
        results["pesq_wb"] = float(pesq_wb)
    except Exception as e:
        results["pesq_wb"] = float("nan")

    # 3. SI-SDR
    try:
        clean_zero_mean = clean - np.mean(clean)
        rest_zero_mean = restored - np.mean(restored)
        alpha = np.dot(clean_zero_mean, rest_zero_mean) / (np.dot(clean_zero_mean, clean_zero_mean) + 1e-8)
        s_target = alpha * clean_zero_mean
        e_noise = rest_zero_mean - s_target
        si_sdr = 10.0 * np.log10((np.sum(s_target ** 2) + 1e-8) / (np.sum(e_noise ** 2) + 1e-8))
        results["si_sdr"] = float(si_sdr)
    except Exception as e:
        results["si_sdr"] = float("nan")

    return results
