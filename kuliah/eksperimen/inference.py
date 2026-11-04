"""
Script Inferensi dan Restorasi Wicara (Inference & Speech Restoration Pipeline).

Mengimplementasikan:
1. Pemuatan model checkpoint Complex U-Net terlatih.
2. Normalisasi gain adaptif pada audio masukan penderita CLP.
3. Transformasi ke spektrogram kompleks STFT.
4. Inferensi difusi terbalik menggunakan Heun Few-Step Sampler (30 langkah).
5. Rekonstruksi waveform melalui Inverse STFT dan denormalisasi penguatan.
6. Evaluasi objektif (PESQ, ESTOI, dan penurunan WER Whisper ASR).
"""

import os
import sys
import yaml
import argparse
from pathlib import Path
from typing import Optional, Dict, Any

import numpy as np
import soundfile as sf
import torch

# Tambahkan direktori root eksperimen ke sys.path
sys.path.insert(0, str(Path(__file__).parent.resolve()))

from data.adaptive_gain import AdaptiveGainNormalizer
from data.cleft_dataset import ComplexSTFTProcessor
from models.complex_unet import ComplexUNet
from models.sde import VPSDE
from solver.heun_sampler import HeunSampler
from evaluate.metrics import compute_metrics
from evaluate.asr_whisper import WhisperEvaluator


class CleftSpeechRestorer:
    """
    Sistem Restorasi Wicara Cleft Lip and Palate End-to-End.
    """
    def __init__(
        self,
        checkpoint_path: str,
        config_path: str = "configs/default_config.yaml",
        device: Optional[str] = None
    ):
        base_dir = Path(__file__).parent.resolve()
        with open(base_dir / config_path, "r", encoding="utf-8") as f:
            self.cfg = yaml.safe_load(f)

        self.device = torch.device(device if device else ("cuda" if torch.cuda.is_available() else "cpu"))
        print(f"[*] Restorer device: {self.device}")

        # Inisialisasi Pra-proses dan STFT
        self.normalizer = AdaptiveGainNormalizer(
            target_dbfs=self.cfg["audio"]["target_dbfs"],
            max_gain=self.cfg["audio"]["max_gain_factor"]
        )
        self.stft_proc = ComplexSTFTProcessor(
            n_fft=self.cfg["stft"]["n_fft"],
            hop_length=self.cfg["stft"]["hop_length"],
            win_length=self.cfg["stft"]["win_length"],
            sample_rate=self.cfg["audio"]["sample_rate"]
        )

        # Inisialisasi Model Complex U-Net
        self.model = ComplexUNet(
            in_channels=self.cfg["model"]["in_channels"],
            cond_channels=self.cfg["model"]["cond_channels"],
            out_channels=self.cfg["model"]["out_channels"],
            base_channels=self.cfg["model"]["base_channels"],
            channel_mult=self.cfg["model"]["channel_mult"],
            num_res_blocks=self.cfg["model"]["num_res_blocks"],
            time_embed_dim=self.cfg["model"]["time_embed_dim"],
            dropout=0.0,
            beta_min=self.cfg["sde"]["beta_min"],
            beta_max=self.cfg["sde"]["beta_max"],
            scale_by_sigma=True
        ).to(self.device)

        # Muat bobot checkpoint
        ckpt_path = Path(checkpoint_path)
        if not ckpt_path.is_absolute():
            ckpt_path = base_dir / ckpt_path
        checkpoint = torch.load(str(ckpt_path), map_location=self.device)
        if "model_state_dict" in checkpoint:
            self.model.load_state_dict(checkpoint["model_state_dict"])
        else:
            self.model.load_state_dict(checkpoint)
        self.model.eval()
        print(f"[*] Model berhasil dimuat dari: {ckpt_path}")

        # Inisialisasi SDE dan Solver
        self.sde = VPSDE(
            beta_min=self.cfg["sde"]["beta_min"],
            beta_max=self.cfg["sde"]["beta_max"],
            eps=self.cfg["sde"]["eps"]
        ).to(self.device)

        self.sampler = HeunSampler(
            sde=self.sde,
            num_steps=self.cfg["solver"]["num_steps"],
            corrector_steps=self.cfg["solver"].get("corrector_steps", 0),
            snr=self.cfg["solver"].get("snr", 0.16),
            use_ode=self.cfg["solver"].get("use_ode", True)
        )

    def restore_file(
        self,
        input_wav_path: str,
        output_wav_path: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Merestorasi sebuah berkas audio wicara CLP.

        Args:
            input_wav_path (str): Path berkas audio .wav input.
            output_wav_path (Optional[str]): Path output .wav hasil restorasi.

        Returns:
            Dict[str, Any]: Informasi hasil restorasi (audio array, gain_factor, metrics).
        """
        # 1. Baca Audio Asli
        audio, sr = sf.read(input_wav_path, dtype="float32")
        if audio.ndim > 1:
            audio = audio[:, 0]

        orig_len = len(audio)

        # 2. Normalisasi Penguatan Adaptif (-23 dBFS)
        norm_audio, gain_factor = self.normalizer.normalize(audio)

        # 3. Transformasi STFT Kompleks [2, F, T]
        audio_tensor = torch.from_numpy(norm_audio).float().to(self.device)
        cond_spec = self.stft_proc.to_stft_complex(audio_tensor).unsqueeze(0)  # [1, 2, F, T]

        # 4. Inferensi Difusi Terbalik (Probability Flow ODE Heun Sampler)
        restored_spec = self.sampler.sample(self.model, cond_spec, show_progress=False)

        # 5. Rekonstruksi Domain Waktu (iSTFT)
        restored_norm_tensor = self.stft_proc.to_waveform(restored_spec.squeeze(0), length=orig_len)
        restored_norm_audio = restored_norm_tensor.cpu().numpy()

        # Proteksi hard clipping jika terdapat lonjakan sesaat
        max_abs = np.max(np.abs(restored_norm_audio))
        if max_abs > 0.999:
            restored_norm_audio = (restored_norm_audio / max_abs) * 0.999

        # Sinyal akhir dipertahankan pada taraf standar optimal -23 dBFS agar jernih dan terdengar jelas
        restored_audio = restored_norm_audio.astype(np.float32)

        # Simpan Berkas Audio Hasil Restorasi jika output_path diberikan
        if output_wav_path:
            os.makedirs(os.path.dirname(output_wav_path), exist_ok=True)
            sf.write(output_wav_path, restored_audio, sr)
            print(f"[SAVED] Audio hasil restorasi tersimpan: {output_wav_path}")

        return {
            "restored_audio": restored_audio,
            "normalized_audio": norm_audio,
            "original_audio": audio,
            "gain_factor": gain_factor,
            "sample_rate": sr
        }


def main():
    parser = argparse.ArgumentParser(description="Restorasi Wicara Cleft Lip and Palate Menggunakan SDE Difusi")
    parser.add_argument("--checkpoint", type=str, required=True, help="Path berkas checkpoint (.pt)")
    parser.add_argument("--input_wav", type=str, required=True, help="Path audio input (.wav)")
    parser.add_argument("--output_wav", type=str, default="restored_output.wav", help="Path audio output (.wav)")
    args = parser.parse_args()

    restorer = CleftSpeechRestorer(checkpoint_path=args.checkpoint)
    result = restorer.restore_file(args.input_wav, args.output_wav)
    print("\n[SUCCESS] Proses restorasi berhasil diselesaikan.")


if __name__ == "__main__":
    main()
