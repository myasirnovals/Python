import base64
import json
import os
import time

import requests

from .config import API_KEY


class GeminiClient:
    def __init__(self, api_key=API_KEY):
        self.api_key = api_key
        self.model_name = None
        self.available_models = []
        self.model_index = -1

    @staticmethod
    def _prioritize_models(models):
        """Urutkan model: flash lebih dulu, lalu model Gemini lain."""
        if not models:
            return []

        flash_models = [m for m in models if "flash" in m]
        non_flash_models = [m for m in models if "flash" not in m]
        return flash_models + non_flash_models

    @staticmethod
    def _is_busy_response(status_code, payload):
        if status_code in (429, 503):
            return True

        if not isinstance(payload, dict):
            return False

        error = payload.get("error") or {}
        message = str(error.get("message", "")).lower()
        status = str(error.get("status", "")).lower()

        busy_keywords = [
            "resource_exhausted",
            "rate limit",
            "quota",
            "overloaded",
            "unavailable",
            "busy",
        ]
        return any(k in message or k in status for k in busy_keywords)

    def _load_candidate_models(self):
        """Muat semua model Gemini yang mendukung generateContent."""
        url = f"https://generativelanguage.googleapis.com/v1beta/models?key={self.api_key}"
        try:
            resp = requests.get(url)
            data = resp.json()
            if "error" in data:
                print(f"❌ Error API Key: {data['error']['message']}")
                return []

            candidates = []
            for model in data.get("models", []):
                name = (model.get("name") or "").replace("models/", "")
                methods = model.get("supportedGenerationMethods") or []
                if "gemini" not in name:
                    continue
                if "embedding" in name:
                    continue
                if "generateContent" not in methods:
                    continue
                candidates.append(name)

            return self._prioritize_models(candidates)
        except Exception as e:
            print(f"❌ Gagal koneksi internet: {e}")
            return []

    def _switch_to_next_model(self):
        """Pindah ke model kandidat berikutnya jika ada."""
        if not self.available_models:
            return False

        if self.model_index + 1 >= len(self.available_models):
            return False

        self.model_index += 1
        self.model_name = self.available_models[self.model_index]
        print(f"      🔁 Fallback ke model: {self.model_name}")
        return True

    def get_active_model(self):
        """Mencari model Gemini yang HIDUP di akun Anda."""
        print("\n🔍 Sedang mencari model AI yang aktif...")
        models = self._load_candidate_models()
        if not models:
            print("❌ Tidak ada model Gemini yang ditemukan.")
            return None

        self.available_models = models
        self.model_index = 0
        self.model_name = self.available_models[self.model_index]
        print(f"✅ Sistem Siap! Menggunakan Otak: {self.model_name}")
        return self.model_name

    def ask(self, prompt_text, image_path=None):
        if not self.model_name:
            if not self.get_active_model():
                return "Error: Tidak ada model."
        headers = {"Content-Type": "application/json"}

        parts = [{"text": prompt_text}]

        # Handle Gambar
        if image_path and os.path.exists(image_path):
            try:
                with open(image_path, "rb") as f:
                    b64_data = base64.b64encode(f.read()).decode("utf-8")
                    parts.append(
                        {
                            "inline_data": {
                                "mime_type": "image/jpeg",
                                "data": b64_data,
                            }
                        }
                    )
            except Exception as e:
                print(f"⚠️ Gagal baca gambar: {e}")

        payload = {"contents": [{"parts": parts}]}

        # Retry Logic + Fallback Model
        for i in range(5):
            try:
                url = (
                    "https://generativelanguage.googleapis.com/v1beta/models/"
                    f"{self.model_name}:generateContent?key={self.api_key}"
                )
                response = requests.post(url, headers=headers, data=json.dumps(payload))
                resp_json = {}
                try:
                    resp_json = response.json()
                except Exception:
                    resp_json = {}

                if response.status_code == 200:
                    try:
                        teks_hasil = resp_json["candidates"][0]["content"]["parts"][0]["text"]

                        # --- MEMBERSIHKAN TANDA KUTIP & BACKTICK ---
                        # Ini akan membuang tanda ' dan ` dari istilah teknis
                        teks_bersih = teks_hasil.replace("'", "").replace("`", "").strip()

                        # 2. FILTER ANTI BASA-BASI (Hapus kalimat pembuka AI)
                        baris = teks_bersih.split("\n")
                        # Jika baris pertama mengandung kata kunci basa-basi, hapus!
                        if len(baris) > 0:
                            kata_kunci = [
                                "berikut adalah",
                                "analisa:",
                                "penjelasan:",
                                "berdasarkan gambar",
                            ]
                            baris_pertama_lower = baris[0].lower()

                            # Cek apakah baris pertama itu cuma pengantar?
                            if any(k in baris_pertama_lower for k in kata_kunci) or baris[0].strip().endswith(
                                ":"
                            ):
                                # Kita buang baris pertama, ambil sisanya
                                baris = baris[1:]

                        # Gabungkan lagi (Hanya pakai \n satu kali agar RAPAT)
                        # strip() membuang spasi kosong di awal/akhir sisa teks
                        teks_final = "\n".join(baris).strip()

                        return teks_final
                    except Exception:
                        return "Error: Format jawaban aneh."
                if self._is_busy_response(response.status_code, resp_json):
                    if self._switch_to_next_model():
                        continue

                    wait = (i + 1) * 5
                    print(f"      ⏳ Server sibuk, menunggu {wait} detik...")
                    time.sleep(wait)
                elif response.status_code == 404:
                    print("      🔄 Model hilang, mencari ulang...")
                    if not self.get_active_model():
                        return "Gagal: Model hilang."
                elif response.status_code in (500, 502):
                    if self._switch_to_next_model():
                        continue
                    wait = (i + 1) * 3
                    time.sleep(wait)
                else:
                    return f"Gagal API: {response.status_code}"
            except Exception:
                time.sleep(2)

        return "Gagal: Server busy (Give up)."
