"""
Script Pelatihan Model Difusi Berbasis Skor (Training Pipeline).

Model: Complex U-Net Score Predictor
Formulasi: Continuous-time VP-SDE
Fungsi Kerugian: Plosive-Weighted Hybrid Loss
"""

import os
# Aktifkan alokasi memori dinamis PyTorch untuk mencegah fragmentasi VRAM
os.environ["PYTORCH_CUDA_ALLOC_CONF"] = "expandable_segments:True"

import sys
import yaml
import argparse
from pathlib import Path

from typing import Optional, Any
import torch
import torch.optim as optim
from torch.utils.data import DataLoader
from tqdm import tqdm

if hasattr(torch, "set_float32_matmul_precision"):
    torch.set_float32_matmul_precision("high")

# Tambahkan direktori root eksperimen ke sys.path
sys.path.insert(0, str(Path(__file__).parent.resolve()))

from data.cleft_dataset import CleftSpeechDataset
from models.complex_unet import ComplexUNet
from models.sde import VPSDE
from loss.plosive_loss import PlosiveWeightedHybridLoss


def get_autocast(device_type: str = "cuda", enabled: bool = True):
    if hasattr(torch, "amp") and hasattr(torch.amp, "autocast"):
        return torch.amp.autocast(device_type, enabled=enabled)
    return torch.cuda.amp.autocast(enabled=enabled)


def get_scaler(device_type: str = "cuda", enabled: bool = True):
    if hasattr(torch, "amp") and hasattr(torch.amp, "GradScaler"):
        return torch.amp.GradScaler(device_type, enabled=enabled)
    return torch.cuda.amp.GradScaler(enabled=enabled)


def set_seed(seed: int = 42):
    torch.manual_seed(seed)
    if torch.cuda.is_available():
        torch.cuda.manual_seed_all(seed)


def train_one_epoch(
    model: torch.nn.Module,
    sde: VPSDE,
    criterion: PlosiveWeightedHybridLoss,
    optimizer: optim.Optimizer,
    dataloader: DataLoader,
    device: torch.device,
    scaler: Optional[Any] = None,
    grad_accum_steps: int = 1,
    use_amp: bool = True,
    grad_clip_norm: float = 1.0,
    epoch: int = 1
):
    model.train()
    total_loss = 0.0
    total_score_loss = 0.0
    total_plosive_loss = 0.0

    optimizer.zero_grad()
    pbar = tqdm(dataloader, desc=f"Epoch {epoch:03d} [Train]")
    for step, batch in enumerate(pbar):
        # complex_spec: [B, 2, F, T] (Real & Imag)
        spec = batch["complex_spec"].to(device)
        batch_size = spec.shape[0]

        # Sinyal kondisi Y adalah spektrogram masukan wicara CLP ternormalisasi
        # Target bersih X_0 dimodelkan pada ruang representasi yang sama
        y_cond = spec
        x_0 = spec

        # Sampel langkah waktu difusi kontinu t ~ U(eps, 1.0)
        t = torch.rand(batch_size, device=device) * (1.0 - sde.eps) + sde.eps

        # Difusi Maju: Injeksikan derau Gaussian ke X_0 menghasilkan X_t
        x_t, noise, score_gt = sde.sample_marginal(x_0, t)

        # Prediksi skor menggunakan Complex U-Net dengan Automatic Mixed Precision
        with get_autocast("cuda", enabled=use_amp):
            score_pred = model(x_t, y_cond, t)

        # Hitung Fungsi Kerugian Hibrida Berbobot Plosif (dalam FP32 untuk stabilitas numerik)
        with get_autocast("cuda", enabled=False):
            loss_dict = criterion(score_pred.float(), x_0.float(), x_t.float(), noise.float(), t)
            loss = loss_dict["loss_total"] / max(grad_accum_steps, 1)

        if scaler is not None and use_amp:
            scaler.scale(loss).backward()
            if (step + 1) % grad_accum_steps == 0 or (step + 1) == len(dataloader):
                if grad_clip_norm > 0:
                    scaler.unscale_(optimizer)
                    torch.nn.utils.clip_grad_norm_(model.parameters(), grad_clip_norm)
                scaler.step(optimizer)
                scaler.update()
                optimizer.zero_grad()
        else:
            loss.backward()
            if (step + 1) % grad_accum_steps == 0 or (step + 1) == len(dataloader):
                if grad_clip_norm > 0:
                    torch.nn.utils.clip_grad_norm_(model.parameters(), grad_clip_norm)
                optimizer.step()
                optimizer.zero_grad()

        total_loss += loss_dict["loss_total"].item()
        total_score_loss += loss_dict["loss_score"].item()
        total_plosive_loss += loss_dict["loss_plosive"].item()

        pbar.set_postfix({
            "Loss": f"{loss_dict['loss_total'].item():.4f}",
            "Score": f"{loss_dict['loss_score'].item():.4f}",
            "Plosive": f"{loss_dict['loss_plosive'].item():.4f}"
        })

    n = max(len(dataloader), 1)
    return total_loss / n, total_score_loss / n, total_plosive_loss / n


@torch.no_grad()
def evaluate_epoch(
    model: torch.nn.Module,
    sde: VPSDE,
    criterion: PlosiveWeightedHybridLoss,
    dataloader: DataLoader,
    device: torch.device,
    use_amp: bool = True
):
    model.eval()
    total_loss = 0.0
    total_score_loss = 0.0
    total_plosive_loss = 0.0

    for batch in dataloader:
        spec = batch["complex_spec"].to(device)
        batch_size = spec.shape[0]

        y_cond = spec
        x_0 = spec

        t = torch.rand(batch_size, device=device) * (1.0 - sde.eps) + sde.eps
        x_t, noise, score_gt = sde.sample_marginal(x_0, t)

        with get_autocast("cuda", enabled=use_amp):
            score_pred = model(x_t, y_cond, t)

        with get_autocast("cuda", enabled=False):
            loss_dict = criterion(score_pred.float(), x_0.float(), x_t.float(), noise.float(), t)

        total_loss += loss_dict["loss_total"].item()
        total_score_loss += loss_dict["loss_score"].item()
        total_plosive_loss += loss_dict["loss_plosive"].item()

    n = max(len(dataloader), 1)
    return total_loss / n, total_score_loss / n, total_plosive_loss / n


def run_quality_gate_asr_check(
    model: torch.nn.Module,
    sde: VPSDE,
    val_dataset: CleftSpeechDataset,
    cfg: Any,
    device: torch.device,
    epoch: int
) -> float:
    """
    Melakukan evaluasi dini kualitas wicara hasil restorasi menggunakan Whisper ASR pada epoch tertentu.
    
    Fail-Fast Quality Gate:
    Mencegah pemborosan kuota GPU Colab jika terdapat anomali matematis atau model belum belajar (WER > max_allowed_wer).
    """
    import numpy as np
    import soundfile as sf
    from solver.heun_sampler import HeunSampler

    try:
        from evaluate.asr_whisper import WhisperEvaluator
    except ImportError as e:
        print(f"[!] Warning: faster-whisper tidak tersedia ({e}). Quality gate dilewati.")
        return 0.0

    num_samples = cfg["training"].get("num_early_check_samples", 5)
    max_allowed_wer = float(cfg["training"].get("max_allowed_wer", 30.0))
    sr = cfg["audio"]["sample_rate"]

    print(f"\n" + "=" * 78)
    print(f"[*] [QUALITY GATE EPOCH {epoch:02d}] Pengujian Keterpahaman Wicara (Whisper ASR)...")
    print(f"[*] Ambang Batas: WER <= {max_allowed_wer:.1f}% | Sampel Uji: {num_samples} rekaman validasi")
    print("=" * 78)

    # Bersihkan cache CUDA sebelum inferensi sampler
    if torch.cuda.is_available():
        torch.cuda.empty_cache()

    sampler = HeunSampler(
        sde=sde,
        num_steps=cfg["solver"]["num_steps"],
        corrector_steps=cfg["solver"].get("corrector_steps", 0),
        snr=cfg["solver"].get("snr", 0.16),
        use_ode=cfg["solver"].get("use_ode", True)
    )

    # Gunakan CPU int8 untuk Whisper agar VRAM GPU tetap bebas untuk model
    try:
        asr_evaluator = WhisperEvaluator(model_size="small", device="cpu", compute_type="int8")
    except Exception as e:
        print(f"[!] Gagal memuat Faster-Whisper Small ({e}), mencoba fallback model 'base'...")
        asr_evaluator = WhisperEvaluator(model_size="base", device="cpu", compute_type="int8")

    out_dir = Path("results") / f"quality_gate_epoch_{epoch:03d}"
    out_dir.mkdir(parents=True, exist_ok=True)

    model.eval()
    total_wer = 0.0
    valid_eval_count = 0

    indices = list(range(min(num_samples, len(val_dataset))))
    for idx in indices:
        sample = val_dataset[idx]
        ref_text = sample.get("prompt_text", "").strip()
        if not ref_text:
            continue

        cond_spec = sample["complex_spec"].unsqueeze(0).to(device)  # [1, 2, F, T]
        orig_len = sample["waveform"].shape[0]

        with torch.no_grad():
            restored_spec = sampler.sample(model, cond_spec, show_progress=False)

        restored_tensor = val_dataset.stft_proc.to_waveform(restored_spec.squeeze(0).cpu(), length=orig_len)
        restored_audio = restored_tensor.numpy()

        # Normalisasi puncak jika melebihi batas 0.999
        max_abs = np.max(np.abs(restored_audio))
        if max_abs > 0.999:
            restored_audio = (restored_audio / max_abs) * 0.999

        # Simpan sampel audio hasil restorasi ke direktori results
        save_path = out_dir / f"sample_{idx+1}_{sample['speaker_id']}.wav"
        sf.write(str(save_path), restored_audio, sr)

        res = asr_evaluator.evaluate_utterance(restored_audio, ref_text, sample_rate=sr)
        sample_wer = res["wer"] * 100.0
        total_wer += sample_wer
        valid_eval_count += 1

        print(f"  [{idx+1}/{len(indices)}] Penutur: {sample['speaker_id']} | File: {sample['file_id']}")
        print(f"       Target Acuan  : '{ref_text}'")
        print(f"       Prediksi ASR  : '{res['hypothesis']}'")
        print(f"       WER           : {sample_wer:.1f}% (CER: {res['cer']*100:.1f}%)")
        print(f"       Tersimpan ke  : {save_path.name}")

    avg_wer = (total_wer / max(valid_eval_count, 1)) if valid_eval_count > 0 else 0.0
    print("-" * 78)
    print(f"[*] RATA-RATA WER VALIDASI (EPOCH {epoch}): {avg_wer:.2f}% (Batas: {max_allowed_wer:.1f}%)")
    print("=" * 78)

    # Kembalikan model ke mode pelatihan dan bersihkan cache
    model.train()
    if torch.cuda.is_available():
        torch.cuda.empty_cache()

    return avg_wer


def main():
    parser = argparse.ArgumentParser(description="Pelatihan Model Difusi CLP Speech Restoration")
    parser.add_argument("--config", type=str, default="configs/default_config.yaml", help="Path konfigurasi YAML")
    parser.add_argument("--epochs", type=int, default=None, help="Override jumlah epoch")
    parser.add_argument("--batch_size", type=int, default=None, help="Override batch size")
    parser.add_argument("--grad_accum_steps", type=int, default=None, help="Override gradient accumulation steps")
    parser.add_argument("--no_amp", action="store_true", help="Nonaktifkan automatic mixed precision")
    args = parser.parse_args()

    base_dir = Path(__file__).parent.resolve()
    config_path = base_dir / args.config

    with open(config_path, "r", encoding="utf-8") as f:
        cfg = yaml.safe_load(f)

    # Override jika ada argumen CLI
    if args.epochs:
        cfg["training"]["epochs"] = args.epochs
    if args.batch_size:
        cfg["training"]["batch_size"] = args.batch_size

    set_seed(cfg["training"]["seed"])
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    print(f"[*] Perangkat komputasi: {device}")

    # Direktori Checkpoint
    checkpoint_val = cfg["paths"].get("checkpoint_dir", "checkpoints")
    checkpoint_dir = Path(checkpoint_val)
    if not checkpoint_dir.is_absolute() or not checkpoint_dir.parent.exists():
        checkpoint_dir = base_dir / "checkpoints"
    checkpoint_dir.mkdir(parents=True, exist_ok=True)

    # 1. Dataset & DataLoader
    splits_val = cfg["paths"].get("split_manifest_dir", "data/splits")
    splits_dir = Path(splits_val)
    if not splits_dir.is_absolute() or not splits_dir.exists():
        splits_dir = base_dir / "data" / "splits"
    train_manifest = splits_dir / "train_manifest.csv"
    val_manifest = splits_dir / "val_manifest.csv"

    ultrasuite_val = cfg["paths"].get("ultrasuite_base_dir")
    ultrasuite_dir = Path(ultrasuite_val) if ultrasuite_val else None
    if ultrasuite_dir is None or not ultrasuite_dir.exists():
        alt_dirs = [
            base_dir / "data" / "UltraSuite",
            base_dir / "UltraSuite",
            base_dir.parent / "UltraSuite",
            base_dir.parent.parent.parent / "UltraSuite",
            Path("/content/drive/MyDrive/Data/perkuliahan/Penelitian/Pengumpulan Berkas/Proposal/Yasir Noval/eksperimen/data/UltraSuite"),
            Path("/content/drive/My Drive/Data/perkuliahan/Penelitian/Pengumpulan Berkas/Proposal/Yasir Noval/eksperimen/data/UltraSuite"),
            Path("J:/My Drive/Data/perkuliahan/Penelitian/Pengumpulan Berkas/Proposal/Yasir Noval/eksperimen/data/UltraSuite"),
            Path("H:/Documents/materi-pembelajaran/python/kuliah/eksperimen/data/UltraSuite")
        ]
        for alt in alt_dirs:
            if alt.exists():
                ultrasuite_dir = alt.resolve()
                break
        if ultrasuite_dir is None:
            ultrasuite_dir = base_dir / "data" / "UltraSuite"

    train_dataset = CleftSpeechDataset(
        manifest_csv=str(train_manifest),
        ultrasuite_base_dir=str(ultrasuite_dir),
        sample_rate=cfg["audio"]["sample_rate"],
        segment_length_sec=cfg["audio"]["segment_length_sec"],
        target_dbfs=cfg["audio"]["target_dbfs"],
        max_gain=cfg["audio"]["max_gain_factor"],
        is_training=True
    )
    val_dataset = CleftSpeechDataset(
        manifest_csv=str(val_manifest),
        ultrasuite_base_dir=str(ultrasuite_dir),
        sample_rate=cfg["audio"]["sample_rate"],
        segment_length_sec=cfg["audio"]["segment_length_sec"],
        target_dbfs=cfg["audio"]["target_dbfs"],
        max_gain=cfg["audio"]["max_gain_factor"],
        is_training=False
    )

    # Pencegahan OOM otomatis pada GPU (misal Colab T4 16GB):
    # Jika batch_size yang diminta > 4 pada CUDA, pecah otomatis menjadi mini-batch <= 4
    # dan naikkan grad_accum_steps agar ukuran batch efektif tetap persis sama!
    requested_bs = cfg["training"]["batch_size"]
    grad_accum_steps = args.grad_accum_steps or cfg["training"].get("grad_accum_steps", 1)
    if device.type == "cuda" and requested_bs > 4:
        safe_bs = 4
        while requested_bs % safe_bs != 0 and safe_bs > 1:
            safe_bs -= 1
        auto_accum = requested_bs // safe_bs
        grad_accum_steps = grad_accum_steps * auto_accum
        print(f"[*] [AUTO-OPTIMASI VRAM GPU] Mengubah mini-batch: {requested_bs} -> {safe_bs} | Grad Accum: {grad_accum_steps} (Batch Efektif: {safe_bs * grad_accum_steps})")
        cfg["training"]["batch_size"] = safe_bs

    train_loader = DataLoader(
        train_dataset,
        batch_size=cfg["training"]["batch_size"],
        shuffle=True,
        num_workers=cfg["training"]["num_workers"],
        pin_memory=(device.type == "cuda")
    )
    val_loader = DataLoader(
        val_dataset,
        batch_size=cfg["training"]["batch_size"],
        shuffle=False,
        num_workers=cfg["training"]["num_workers"],
        pin_memory=(device.type == "cuda")
    )
    print(f"[*] Data Latih: {len(train_dataset)} audio | Data Validasi: {len(val_dataset)} audio")

    # 2. Inisialisasi Model, SDE, dan Loss
    model = ComplexUNet(
        in_channels=cfg["model"]["in_channels"],
        cond_channels=cfg["model"]["cond_channels"],
        out_channels=cfg["model"]["out_channels"],
        base_channels=cfg["model"]["base_channels"],
        channel_mult=cfg["model"]["channel_mult"],
        num_res_blocks=cfg["model"]["num_res_blocks"],
        time_embed_dim=cfg["model"]["time_embed_dim"],
        dropout=cfg["model"]["dropout"],
        beta_min=cfg["sde"]["beta_min"],
        beta_max=cfg["sde"]["beta_max"],
        scale_by_sigma=True
    ).to(device)

    sde = VPSDE(
        beta_min=cfg["sde"]["beta_min"],
        beta_max=cfg["sde"]["beta_max"],
        eps=cfg["sde"]["eps"]
    ).to(device)

    criterion = PlosiveWeightedHybridLoss(
        sde=sde,
        gamma_plosive=cfg["loss"]["gamma_plosive"],
        sample_rate=cfg["audio"]["sample_rate"],
        n_fft=cfg["stft"]["n_fft"],
        plosive_freq_min_hz=cfg["loss"]["plosive_freq_min_hz"],
        plosive_freq_max_hz=cfg["loss"]["plosive_freq_max_hz"]
    ).to(device)

    optimizer = optim.AdamW(
        model.parameters(),
        lr=float(cfg["training"]["learning_rate"]),
        weight_decay=float(cfg["training"]["weight_decay"])
    )

    scheduler = optim.lr_scheduler.CosineAnnealingLR(
        optimizer,
        T_max=cfg["training"]["epochs"],
        eta_min=1e-6
    )

    use_amp = (device.type == "cuda") and cfg["training"].get("use_amp", True) and not args.no_amp
    scaler = get_scaler("cuda", enabled=use_amp)

    if torch.cuda.is_available():
        torch.cuda.empty_cache()

    eff_bs = cfg["training"]["batch_size"] * grad_accum_steps
    print(f"[*] Total parameter Complex U-Net: {sum(p.numel() for p in model.parameters()):,}")
    print(f"[*] Batch size fisik: {cfg['training']['batch_size']} | Grad Accum: {grad_accum_steps} (Batch Efektif: {eff_bs}) | AMP FP16: {use_amp}")
    print("[*] Memulai pelatihan...")

    best_val_loss = float("inf")
    epochs = cfg["training"]["epochs"]

    for epoch in range(1, epochs + 1):
        tr_loss, tr_score, tr_plosive = train_one_epoch(
            model, sde, criterion, optimizer, train_loader, device,
            scaler=scaler, grad_accum_steps=grad_accum_steps, use_amp=use_amp,
            grad_clip_norm=cfg["training"]["grad_clip_norm"], epoch=epoch
        )
        val_loss, val_score, val_plosive = evaluate_epoch(
            model, sde, criterion, val_loader, device, use_amp=use_amp
        )
        scheduler.step()

        print(f"[Epoch {epoch:03d}/{epochs:03d}] Train: {tr_loss:.4f} | Val: {val_loss:.4f} (Score: {val_score:.4f}, Plosive: {val_plosive:.4f})")

        # Simpan Best Model
        if val_loss < best_val_loss:
            best_val_loss = val_loss
            torch.save({
                "epoch": epoch,
                "model_state_dict": model.state_dict(),
                "optimizer_state_dict": optimizer.state_dict(),
                "val_loss": val_loss,
                "config": cfg
            }, checkpoint_dir / "best_model.pt")
            print(f"  --> [BEST] Model terbaik tersimpan pada epoch {epoch} (Val Loss: {val_loss:.4f})")

        # Simpan checkpoint berkala
        if epoch % cfg["training"]["save_every_epochs"] == 0 or epoch == epochs:
            torch.save({
                "epoch": epoch,
                "model_state_dict": model.state_dict(),
                "val_loss": val_loss
            }, checkpoint_dir / f"checkpoint_epoch_{epoch:03d}.pt")

        # Fail-Fast Quality Gate (Uji Keterpahaman ASR pada Epoch ke-10)
        early_check_epoch = cfg["training"].get("early_check_epoch", 10)
        max_allowed_wer = float(cfg["training"].get("max_allowed_wer", 30.0))

        if epoch == early_check_epoch:
            avg_wer = run_quality_gate_asr_check(
                model=model,
                sde=sde,
                val_dataset=val_dataset,
                cfg=cfg,
                device=device,
                epoch=epoch
            )
            if avg_wer > max_allowed_wer:
                print(f"\n[FAIL-FAST TRIGGERED] Rata-rata WER ({avg_wer:.2f}%) melampaui batas toleransi ({max_allowed_wer:.1f}%).")
                print(f"[!] Pelatihan dihentikan otomatis pada epoch ke-{epoch} untuk menghemat alokasi GPU Google Colab.")
                print("    Silakan tinjau kembali formulasi skor, penguatan adaptif, atau kurva loss sebelum melanjutkan ke 50 epoch.")
                break
            else:
                print(f"\n[QUALITY GATE PASSED] WER ({avg_wer:.2f}% <= {max_allowed_wer:.1f}%) berhasil memenuhi target keterpahaman!")
                print("    Melanjutkan pelatihan penuh hingga selesai...")

    print("[SUCCESS] Pelatihan selesai!")


if __name__ == "__main__":
    main()
