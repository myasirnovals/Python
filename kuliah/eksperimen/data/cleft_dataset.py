"""
PyTorch Dataset & DataLoader untuk Wicara Cleft Lip and Palate.

Mengimplementasikan:
1. Pemuatan berkas audio dari manifest CSV.
2. Penyeragaman frekuensi cuplikan ke 22.050 Hz (mono).
3. Normalisasi penguatan adaptif dinamis (Adaptive Gain Normalization ke -23 dBFS).
4. Transformasi Short-Time Fourier Transform Kompleks (Complex STFT):
   - Jendela Hann 512 cuplikan
   - Hop length 128 cuplikan (overlap 75%)
   - NFFT 512 titik (menghasilkan F = 257 bin frekuensi)
   - Kanal tensor masukan: [2, F, T] (Real & Imaginary)
5. Inverse STFT (iSTFT) untuk rekonstruksi domain waktu gelombang (waveform).
"""

import os
import csv
from pathlib import Path
from typing import Dict, Any, Optional, Tuple

import numpy as np
import soundfile as sf
import torch
from torch.utils.data import Dataset, DataLoader

from .adaptive_gain import AdaptiveGainNormalizer


class ComplexSTFTProcessor:
    """
    Kelas Utilitas untuk Transformasi STFT Kompleks dan Inverse STFT.
    """
    def __init__(
        self,
        n_fft: int = 512,
        hop_length: int = 128,
        win_length: int = 512,
        sample_rate: int = 22050
    ):
        self.n_fft = n_fft
        self.hop_length = hop_length
        self.win_length = win_length
        self.sample_rate = sample_rate
        self.window = torch.hann_window(win_length)

    def to_stft_complex(self, waveform: torch.Tensor) -> torch.Tensor:
        """
        Mengubah waveform waktu 1D [T_samples] atau 2D [B, T_samples]
        menjadi representasi 2-kanal real/imag: [2, F, T_frames] atau [B, 2, F, T_frames].
        """
        is_batched = waveform.dim() == 2
        if not is_batched:
            waveform = waveform.unsqueeze(0)

        window = self.window.to(waveform.device)
        # torch.stft return complex tensor: [B, F, T]
        stft_c = torch.stft(
            waveform,
            n_fft=self.n_fft,
            hop_length=self.hop_length,
            win_length=self.win_length,
            window=window,
            center=True,
            normalized=False,
            onesided=True,
            return_complex=True
        )

        # Pisahkan menjadi komponen real dan imag: [B, 2, F, T]
        stft_real = torch.real(stft_c)
        stft_imag = torch.imag(stft_c)
        stft_ri = torch.stack([stft_real, stft_imag], dim=1)

        if not is_batched:
            stft_ri = stft_ri.squeeze(0)

        return stft_ri

    def to_waveform(self, stft_ri: torch.Tensor, length: Optional[int] = None) -> torch.Tensor:
        """
        Mengubah representasi [2, F, T] atau [B, 2, F, T] kembali ke waveform [T_samples] atau [B, T_samples].
        """
        is_batched = stft_ri.dim() == 4
        if not is_batched:
            stft_ri = stft_ri.unsqueeze(0)

        window = self.window.to(stft_ri.device)
        stft_c = torch.complex(stft_ri[:, 0, :, :], stft_ri[:, 1, :, :])

        waveform = torch.istft(
            stft_c,
            n_fft=self.n_fft,
            hop_length=self.hop_length,
            win_length=self.win_length,
            window=window,
            center=True,
            normalized=False,
            onesided=True,
            length=length
        )

        if not is_batched:
            waveform = waveform.squeeze(0)

        return waveform


class CleftSpeechDataset(Dataset):
    """
    PyTorch Dataset untuk Memuat Audio Cleft UltraSuite dan Mengekstrak Spektrogram Kompleks.
    """
    def __init__(
        self,
        manifest_csv: str,
        ultrasuite_base_dir: str,
        sample_rate: int = 22050,
        segment_length_sec: Optional[float] = 2.0,
        target_dbfs: float = -23.0,
        max_gain: float = 90.0,
        is_training: bool = True
    ):
        super().__init__()
        self.manifest_csv = Path(manifest_csv)
        self.ultrasuite_base_dir = Path(ultrasuite_base_dir)
        self.sample_rate = sample_rate
        self.segment_samples = int(segment_length_sec * sample_rate) if segment_length_sec else None
        self.is_training = is_training

        self.normalizer = AdaptiveGainNormalizer(target_dbfs=target_dbfs, max_gain=max_gain)
        self.stft_proc = ComplexSTFTProcessor(n_fft=512, hop_length=128, win_length=512, sample_rate=sample_rate)

        # Muat rekaman dari manifest
        self.samples = []
        with open(self.manifest_csv, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for r in reader:
                self.samples.append(r)

    def __len__(self) -> int:
        return len(self.samples)

    def __getitem__(self, idx: int) -> Dict[str, Any]:
        info = self.samples[idx]
        rel_audio_path = info["audio_path"]
        full_audio_path = self.ultrasuite_base_dir / rel_audio_path

        # Baca berkas audio WAV
        audio, sr = sf.read(str(full_audio_path), dtype="float32")
        if audio.ndim > 1:
            audio = audio[:, 0]  # Ambil mono kanal pertama

        # Terapkan Normalisasi Penguatan Adaptif (-23 dBFS)
        norm_audio, gain_factor = self.normalizer.normalize(audio)

        # Pemotongan / Padding ke panjang tetap (Segment Length) saat pelatihan
        if self.segment_samples is not None:
            total_samples = len(norm_audio)
            if total_samples >= self.segment_samples:
                if self.is_training:
                    # Ambil segmen acak untuk variasi data latih
                    max_start = total_samples - self.segment_samples
                    start = np.random.randint(0, max_start + 1)
                else:
                    # Ambil bagian tengah untuk validasi yang deterministik
                    start = (total_samples - self.segment_samples) // 2
                norm_audio = norm_audio[start:start + self.segment_samples]
            else:
                # Padding jika audio lebih pendek dari segmen target
                pad_width = self.segment_samples - total_samples
                norm_audio = np.pad(norm_audio, (0, pad_width), mode="constant")

        # Konversi ke PyTorch Tensor
        audio_tensor = torch.from_numpy(norm_audio).float()

        # Ekstraksi Spektrogram Kompleks [2, F, T]
        complex_spec = self.stft_proc.to_stft_complex(audio_tensor)

        return {
            "complex_spec": complex_spec,           # Tensor [2, 257, T]
            "waveform": audio_tensor,               # Tensor [T_samples]
            "gain_factor": gain_factor,             # float
            "speaker_id": info["speaker_id"],
            "cleft_type": info["cleft_type"],
            "prompt_text": info["prompt_text"],
            "file_id": info["file_id"]
        }


def get_dataloader(
    manifest_csv: str,
    ultrasuite_base_dir: str,
    batch_size: int = 8,
    is_training: bool = True,
    num_workers: int = 0
) -> DataLoader:
    """Fungsi pembantu membuat DataLoader PyTorch standar."""
    dataset = CleftSpeechDataset(
        manifest_csv=manifest_csv,
        ultrasuite_base_dir=ultrasuite_base_dir,
        is_training=is_training
    )
    return DataLoader(
        dataset,
        batch_size=batch_size,
        shuffle=is_training,
        num_workers=num_workers,
        pin_memory=torch.cuda.is_available()
    )


if __name__ == "__main__":
    script_dir = Path(__file__).parent.resolve()
    test_manifest = script_dir / "splits" / "val_manifest.csv"
    base_dir = script_dir / "UltraSuite"
    if not base_dir.exists():
        base_dir = script_dir.parent / "UltraSuite"

    if test_manifest.exists():
        print(f"[*] Manifest ditemukan: {test_manifest}")
        if base_dir.exists():
            ds = CleftSpeechDataset(str(test_manifest), str(base_dir), segment_length_sec=2.0, is_training=False)
            print(f"Dataset length: {len(ds)}")
            sample = ds[0]
            print(f"Sample 0 Speaker   : {sample['speaker_id']} ({sample['cleft_type']})")
            print(f"Gain factor        : {sample['gain_factor']:.2f}x")
            print(f"Waveform shape     : {sample['waveform'].shape}")
            print(f"Complex Spec shape : {sample['complex_spec'].shape} ([Real/Imag, Freq, Time])")
            print("[SUCCESS] CleftSpeechDataset teruji bekerja dengan baik!")
        else:
            print(f"[INFO] Direktori UltraSuite ({base_dir}) belum tersedia di mesin lokal.")
    else:
        print("[INFO] Jalankan split_speakers.py terlebih dahulu.")
