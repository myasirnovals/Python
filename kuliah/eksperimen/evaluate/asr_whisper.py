"""
Modul Evaluasi Keterpahaman Hilir ASR (Downstream Whisper ASR Evaluation).

Mengukur tingkat Word Error Rate (WER) dan Character Error Rate (CER)
antara transkrip acuan ground truth UltraSuite dengan hasil transkripsi
model fondasi OpenAI Whisper (Base / Small) sebelum dan sesudah restorasi.
"""

import os
import re
from typing import List, Dict, Tuple, Any
import numpy as np
from faster_whisper import WhisperModel


def normalize_text(text: str) -> str:
    """Normalisasi teks: huruf kecil, hilangkan tanda baca, hapus spasi berlebih."""
    text = text.lower()
    text = re.sub(r"[^\w\s]", "", text)
    text = re.sub(r"\s+", " ", text).strip()
    return text


def compute_levenshtein_distance(ref_tokens: List[str], hyp_tokens: List[str]) -> int:
    """Menghitung jarak Levenshtein antara token referensi dan hipotesis."""
    n, m = len(ref_tokens), len(hyp_tokens)
    dp = [[0] * (m + 1) for _ in range(n + 1)]

    for i in range(n + 1):
        dp[i][0] = i
    for j in range(m + 1):
        dp[0][j] = j

    for i in range(1, n + 1):
        for j in range(1, m + 1):
            if ref_tokens[i - 1] == hyp_tokens[j - 1]:
                dp[i][j] = dp[i - 1][j - 1]
            else:
                dp[i][j] = 1 + min(dp[i - 1][j], dp[i][j - 1], dp[i - 1][j - 1])

    return dp[n][m]


def compute_wer_cer(reference: str, hypothesis: str) -> Tuple[float, float]:
    """
    Menghitung Word Error Rate (WER) dan Character Error Rate (CER).
    """
    ref_norm = normalize_text(reference)
    hyp_norm = normalize_text(hypothesis)

    ref_words = ref_norm.split()
    hyp_words = hyp_norm.split()

    # Hitung WER
    if len(ref_words) == 0:
        wer = 0.0 if len(hyp_words) == 0 else 1.0
    else:
        dist_w = compute_levenshtein_distance(ref_words, hyp_words)
        wer = dist_w / len(ref_words)

    # Hitung CER
    ref_chars = list(ref_norm.replace(" ", ""))
    hyp_chars = list(hyp_norm.replace(" ", ""))
    if len(ref_chars) == 0:
        cer = 0.0 if len(hyp_chars) == 0 else 1.0
    else:
        dist_c = compute_levenshtein_distance(ref_chars, hyp_chars)
        cer = dist_c / len(ref_chars)

    return float(wer), float(cer)


class WhisperEvaluator:
    """
    Evaluator ASR Menggunakan Faster-Whisper.
    """
    def __init__(self, model_size: str = "small", device: str = "cpu", compute_type: str = "int8"):
        self.model = WhisperModel(model_size, device=device, compute_type=compute_type)

    def transcribe_audio_file(self, audio_input: Any, language: str = "en", sample_rate: int = 16000) -> str:
        """
        Mentranskripsi berkas audio atau array numpy dan mengembalikan teks hasil inferensi.
        Mendukung audio_input berupa:
        - str / Path (path berkas .wav)
        - np.ndarray (1D waveform float32)

        Audio secara otomatis disesuaikan ke format mono 16.000 Hz float32 dan dikirim langsung
        ke self.model.transcribe() sebagai numpy array untuk menghindari pemanggilan internal
        av.open() yang memicu error 'metadata_errors' pada versi PyAV terbaru di Google Colab.
        """
        import soundfile as sf
        import scipy.signal

        if isinstance(audio_input, (str, bytes, os.PathLike)):
            audio, sr = sf.read(str(audio_input), dtype="float32")
            if audio.ndim > 1:
                audio = audio[:, 0]
            if sr != 16000:
                num_samples_16k = int(len(audio) * 16000 / sr)
                audio = scipy.signal.resample(audio, num_samples_16k)
        elif isinstance(audio_input, np.ndarray):
            audio = audio_input.astype(np.float32)
            if audio.ndim > 1:
                audio = audio[:, 0]
            if sample_rate != 16000:
                num_samples_16k = int(len(audio) * 16000 / sample_rate)
                audio = scipy.signal.resample(audio, num_samples_16k)
        else:
            raise TypeError(f"audio_input harus berupa str path atau np.ndarray, didapat {type(audio_input)}")

        # Normalisasi penguatan amplitudo jika melampaui rentang [-1, 1]
        max_abs = np.max(np.abs(audio))
        if max_abs > 1.0:
            audio = audio / max_abs

        segments, _ = self.model.transcribe(
            audio,
            language=language,
            beam_size=5,
            vad_filter=True,
            condition_on_previous_text=False,
            repetition_penalty=1.1
        )
        transcript = " ".join([seg.text.strip() for seg in segments])
        return transcript

    def evaluate_utterance(self, audio_input: Any, ground_truth_text: str, sample_rate: int = 16000) -> Dict[str, Any]:
        """Evaluasi satu rekaman audio terhadap ground truth teks."""
        hyp_text = self.transcribe_audio_file(audio_input, language="en", sample_rate=sample_rate)
        wer, cer = compute_wer_cer(ground_truth_text, hyp_text)
        return {
            "ground_truth": ground_truth_text,
            "hypothesis": hyp_text,
            "wer": wer,
            "cer": cer
        }
