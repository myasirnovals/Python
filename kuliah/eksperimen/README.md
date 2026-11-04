# Implementasi Eksperimen Komputasi: Score-Based Audio Diffusion Model untuk Restorasi Ujaran Cleft Lip and Palate

Repositori kode sumber eksperimen penelitian tugas akhir:
**"Restorasi Inteligibilitas Ujaran Pasien Cleft Lip and Palate Menggunakan Score-Based Audio Diffusion Model Berbasis Adaptive Gain Normalization"**

- **Peneliti**: Muhamad Yasir Noval (NIM: 2350081004)
- **Program Studi**: Informatika, Universitas Jenderal Achmad Yani (UNJANI)
- **Dosen Pembimbing**: Dr. Agus Komarudin, S.Kom., M.T.

---

## 📁 Struktur Direktori Eksperimen

```text
eksperimen/
├── configs/
│   └── default_config.yaml         # Konfigurasi hyperparameter (Audio, STFT, SDE, U-Net, Loss, Solver)
├── data/
│   ├── adaptive_gain.py            # Modul normalisasi penguatan dinamis (-23 dBFS)
│   ├── cleft_dataset.py            # PyTorch Dataset & STFT Processor
│   ├── split_speakers.py           # Script partisi bebas penutur (Speaker-Independent Split)
│   └── splits/                     # Manifest subset partisi (Train 15, Val 3, Test 3)
│       ├── train_manifest.csv
│       ├── val_manifest.csv
│       ├── test_manifest.csv
│       └── split_summary.md
├── models/
│   ├── complex_modules.py          # Lapisan Complex Conv2d, Complex BatchNorm, Sinusoidal Embedding
│   ├── complex_unet.py             # Arsitektur Multi-Scale Complex U-Net Score Predictor
│   └── sde.py                      # Formulasi continuous-time Variance-Preserving SDE (VP-SDE)
├── loss/
│   └── plosive_loss.py             # Plosive-Weighted Hybrid Loss (L_score + gamma * L_plosive)
├── solver/
│   └── heun_sampler.py             # Predictor-corrector Heun reverse SDE sampler (30 langkah)
├── evaluate/
│   ├── metrics.py                  # Kalkulasi metrik objektif akustik (PESQ, ESTOI, SI-SDR)
│   └── asr_whisper.py              # Evaluasi keterpahaman hilir ASR Whisper (WER & CER)
├── checkpoints/                    # Direktori penyimpanan bobot model terbaik (.pt)
├── results/                        # Direktori penyimpanan audio hasil restorasi dan log metrik
├── train.py                        # Script utama pelatihan model difusi
├── inference.py                    # Script inferensi restorasi wicara
├── requirements.txt                # Daftar pustaka dependensi Python
└── README.md                       # Dokumentasi teknis eksperimen
```

---

## ⚙️ Persyaratan Lingkungan & Instalasi

Disarankan menggunakan **Python 3.11** untuk kompatibilitas penuh dengan PyTorch CUDA di lingkungan Windows.

```powershell
# Pasang dependensi utama
pip install -r requirements.txt
```

---

## 🚀 Alur Kerja Eksperimen (Workflow)

### 1. Pembagian Dataset Bebas Penutur (*Speaker-Independent Split*)
Mempartisi 21 penutur korpus UltraSuite berlabel SLT menjadi 15 penutur Train, 3 penutur Val, dan 3 penutur Test:
```powershell
python data/split_speakers.py
```
Hasil partisi tersimpan di folder `data/splits/`.

### 2. Pelatihan Model (*Training*)
Menjalankan pelatihan jaringan Complex U-Net dengan modulasi waktu kontinu dan *Plosive-Weighted Loss*:
```powershell
python train.py --config configs/default_config.yaml
```
Argumen tambahan yang tersedia:
- `--epochs <N>`: Menentukan jumlah epoch (default: 100).
- `--batch_size <B>`: Menentukan ukuran batch (default: 8).

Model terbaik secara otomatis disimpan pada `checkpoints/best_model.pt`.

### 3. Inferensi & Restorasi Wicara (*Inference*)
Melakukan restorasi wicara pada rekaman audio uji:
```powershell
python inference.py --checkpoint checkpoints/best_model.pt --input_wav path/to/cleft_audio.wav --output_wav results/restored_speech.wav
```

### 4. Evaluasi Kualitas & Keterpahaman (*Evaluation*)
Sistem mengukur:
- Kualitas persepsi pendengaran: **PESQ** (target $> 3.0$)
- Keterpahaman objektif: **ESTOI** (target $> 0.85$)
- Penurunan kesalahan pengenalan kata: **Word Error Rate (WER)** pada sistem OpenAI Whisper.
