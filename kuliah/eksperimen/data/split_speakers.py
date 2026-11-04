"""
Skrip Pembagian Dataset Bebas Penutur (Speaker-Independent Partitioning).

Membagi korpus wicara UltraSuite Cleft ke dalam subset:
- TRAIN : 15 Penutur (Bebas penutur)
- VAL   : 3 Penutur (Unseen speakers)
- TEST  : 3 Penutur (Unseen speakers)

Sesuai protokol evaluasi ilmiah Proposal Penelitian Tugas Akhir:
Mahasiswa: Muhamad Yasir Noval (2350081004) - Informatika UNJANI
Pembimbing: Dr. Agus Komarudin, S.Kom., M.T.
"""

import os
import csv
import wave
from pathlib import Path
from collections import defaultdict, Counter


def build_manifest_and_splits(
    ultrasuite_base_dir: Path,
    splits_output_dir: Path,
    master_manifest_path: Path
):
    core_dir = ultrasuite_base_dir / "core-cleft"
    labels_dir = ultrasuite_base_dir / "labels-cleft" / "slt_labels"
    doc_speakers_file = core_dir / "doc" / "speakers"

    print(f"[*] Base Dataset Directory: {ultrasuite_base_dir}")
    print(f"[*] Splits Output Directory: {splits_output_dir}")

    # 1. Parsing Metadata Penutur dari doc/speakers
    speakers_meta = {}
    if doc_speakers_file.exists():
        with open(doc_speakers_file, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f, delimiter="\t")
            for row in reader:
                spk_id = row.get("SPEAKER-ID", "").strip()
                if spk_id:
                    speakers_meta[spk_id] = {
                        "gender": row.get("GENDER", "").strip(),
                        "age_years": row.get("AGE", "").strip(),
                        "age_y": row.get("AGE-Y", "").strip(),
                        "age_m": row.get("AGE-M", "").strip(),
                        "cleft_type": row.get("CLEFT-TYPE", "").strip(),
                        "other_medical": row.get("OTHER-MEDICAL", "").strip(),
                        "medical_diagnosis": row.get("OTHER-MEDICAL-DIAGNOSIS", "").strip(),
                    }
        print(f"[OK] Metadata dimuat untuk {len(speakers_meta)} penutur.")
    else:
        print(f"[!] Warning: File {doc_speakers_file} tidak ditemukan!")

    # 2. Indeks Anotasi SLT TextGrid
    slt_map = defaultdict(list)
    if labels_dir.exists():
        for tg in labels_dir.glob("*.TextGrid"):
            parts = tg.stem.split("-")
            if len(parts) >= 4:
                spk = parts[0]
                session = parts[1]
                file_id = parts[2]
                key = (spk, session, file_id)
                rel_tg = tg.relative_to(ultrasuite_base_dir).as_posix()
                slt_map[key].append(rel_tg)
        print(f"[OK] Terindeks {sum(len(v) for v in slt_map.values())} SLT TextGrid pada {len(slt_map)} rekaman.")

    # 3. Pindai Berkas Audio WAV dan TXT Prompts
    core_speakers_dir = core_dir / "core"
    wav_files = sorted(list(core_speakers_dir.glob("*/*/*.wav")))
    print(f"[OK] Ditemukan {len(wav_files)} berkas audio WAV.")

    manifest_rows = []
    for wav_path in wav_files:
        rel_wav = wav_path.relative_to(ultrasuite_base_dir).as_posix()
        speaker_id = wav_path.parent.parent.name
        session = wav_path.parent.name
        file_id = wav_path.stem

        txt_path = wav_path.with_suffix(".txt")
        prompt_text = ""
        timestamp = ""

        if txt_path.exists():
            try:
                with open(txt_path, "r", encoding="utf-8", errors="replace") as tf:
                    lines = [l.strip() for l in tf.readlines()]
                    if len(lines) > 0:
                        prompt_text = lines[0]
                    if len(lines) > 1:
                        timestamp = lines[1]
            except Exception:
                pass

        # Ambil durasi dan spesifikasi audio
        duration = 0.0
        sample_rate = 22050
        channels = 1
        try:
            with wave.open(str(wav_path), "rb") as wf:
                sample_rate = wf.getframerate()
                channels = wf.getnchannels()
                frames = wf.getnframes()
                duration = round(frames / float(sample_rate), 3) if sample_rate > 0 else 0.0
        except Exception as e:
            print(f"[!] Galat membaca {wav_path}: {e}")

        spk_info = speakers_meta.get(speaker_id, {})
        slt_list = slt_map.get((speaker_id, session, file_id), [])

        row = {
            "speaker_id": speaker_id,
            "session": session,
            "file_id": file_id,
            "prompt_text": prompt_text,
            "duration_sec": duration,
            "sample_rate": sample_rate,
            "channels": channels,
            "gender": spk_info.get("gender", ""),
            "age_years": spk_info.get("age_years", ""),
            "cleft_type": spk_info.get("cleft_type", "Unknown"),
            "other_medical": spk_info.get("other_medical", "no"),
            "medical_diagnosis": spk_info.get("medical_diagnosis", "None"),
            "has_slt_label": "yes" if slt_list else "no",
            "num_slt_labels": len(slt_list),
            "slt_label_paths": ";".join(slt_list),
            "audio_path": rel_wav,
            "recorded_timestamp": timestamp
        }
        manifest_rows.append(row)

    # 4. Simpan Master Manifest CSV
    fieldnames = list(manifest_rows[0].keys())
    master_manifest_path.parent.mkdir(parents=True, exist_ok=True)
    with open(master_manifest_path, "w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(manifest_rows)
    print(f"[SAVED] Master manifest tersimpan: {master_manifest_path} ({len(manifest_rows)} baris)")

    # 5. Partisi Bebas Penutur (Speaker-Independent Split) Sesuai Proposal
    # 21 penutur inti wicara sumbing murni tanpa komorbiditas sindrom lain
    train_speakers = {"01M", "03F", "06M", "07M", "11M", "15F", "16M", "24M", "28F", "30F", "31F", "32M", "34M", "35M", "36M"}
    val_speakers = {"17F", "25M", "33M"}
    test_speakers = {"09M", "12F", "14F"}

    # Pisahkan baris
    train_rows = [r for r in manifest_rows if r["speaker_id"] in train_speakers]
    val_rows = [r for r in manifest_rows if r["speaker_id"] in val_speakers]
    test_rows = [r for r in manifest_rows if r["speaker_id"] in test_speakers]

    splits_output_dir.mkdir(parents=True, exist_ok=True)
    splits = [
        ("train_manifest.csv", train_rows),
        ("val_manifest.csv", val_rows),
        ("test_manifest.csv", test_rows)
    ]

    for fname, rows in splits:
        out_csv = splits_output_dir / fname
        with open(out_csv, "w", encoding="utf-8", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(rows)
        print(f"[SAVED] {fname} ({len(rows)} baris) tersimpan di {out_csv}")

    # 6. Buat Ringkasan Statistik Partisi (split_summary.md)
    def summarize_set(rows):
        spks = sorted(list(set(r["speaker_id"] for r in rows)))
        dur = sum(float(r["duration_sec"]) for r in rows)
        clefts = Counter(r["cleft_type"] for r in rows)
        return len(spks), ", ".join(spks), len(rows), dur, clefts

    train_n_spk, train_spks, train_n_rec, train_dur, train_clefts = summarize_set(train_rows)
    val_n_spk, val_spks, val_n_rec, val_dur, val_clefts = summarize_set(val_rows)
    test_n_spk, test_spks, test_n_rec, test_dur, test_clefts = summarize_set(test_rows)

    summary_content = f"""# Ringkasan Partisi Dataset Bebas Penutur (Speaker-Independent Split)

Sesuai dengan protokol evaluasi Proposal Penelitian TA 1.

| Subset | Jumlah Penutur | Daftar Speaker ID | Total Rekaman Audio | Total Durasi (Detik) |
|:---|:---:|:---|:---:|:---:|
| **TRAIN** | {train_n_spk} | `{train_spks}` | **{train_n_rec}** | {train_dur:.1f} s (~{train_dur/60:.1f} m) |
| **VAL** | {val_n_spk} | `{val_spks}` | **{val_n_rec}** | {val_dur:.1f} s (~{val_dur/60:.1f} m) |
| **TEST** | {test_n_spk} | `{test_spks}` | **{test_n_rec}** | {test_dur:.1f} s (~{test_dur/60:.1f} m) |

### Sebaran Tipe Cleft per Subset:

| Subset | CP (Cleft Palate) | UCLP (Unilateral) | BCLP (Bilateral) |
|:---|:---:|:---:|:---:|
| **TRAIN** | {train_clefts.get('CP', 0)} | {train_clefts.get('UCLP', 0)} | {train_clefts.get('BCLP', 0)} |
| **VAL** | {val_clefts.get('CP', 0)} | {val_clefts.get('UCLP', 0)} | {val_clefts.get('BCLP', 0)} |
| **TEST** | {test_clefts.get('CP', 0)} | {test_clefts.get('UCLP', 0)} | {test_clefts.get('BCLP', 0)} |
"""
    summary_path = splits_output_dir / "split_summary.md"
    with open(summary_path, "w", encoding="utf-8") as f:
        f.write(summary_content)
    print(f"[SAVED] Ringkasan partisi tersimpan di {summary_path}")


if __name__ == "__main__":
    script_dir = Path(__file__).parent.resolve()
    base_dir = script_dir / "UltraSuite"
    splits_dir = script_dir / "splits"
    master_csv = base_dir / "dataset_manifest.csv"

    # Juga simpan master manifest di root eksperimen
    root_master_csv = script_dir.parent / "dataset_manifest.csv"

    build_manifest_and_splits(base_dir, splits_dir, master_csv)

    # Buat salinan di root jika diperlukan
    if master_csv.exists() and not root_master_csv.exists():
        import shutil
        shutil.copy(master_csv, root_master_csv)
        print(f"[SAVED] Salinan master manifest di root: {root_master_csv}")
