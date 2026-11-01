import os
import re


class PromptBuilder:
    """Build and centralize prompt templates used by AI workflows."""

    DEFAULT_JUDUL_LAPORAN = "PrakSpeechProcessing_2350081004_MUHAMAD YASIR NOVAL_A_Modul1"
    DEFAULT_MATERI_MODUL = "Modul 1 Prak. Speech Processing"

    @classmethod
    def resolve_identifiers(cls, cover_data=None, modul_path=None, modul_text=""):
        """Membentuk judul_laporan dan materi_modul secara dinamis dari data cover / modul."""
        cover_data = cover_data or {}
        mk = (cover_data.get("mata_kuliah") or "").strip()
        mk_clean = re.sub(r"[^a-zA-Z0-9]", "", mk)
        nim = (cover_data.get("nim") or "").strip()
        nama = (cover_data.get("nama") or "").strip()
        modul_num = (cover_data.get("nomor_modul") or "").strip()
        judul_modul = (cover_data.get("judul") or "").strip()

        if mk_clean and nim and nama and modul_num:
            judul_laporan = f"Prak{mk_clean}_{nim}_{nama}_A_Modul{modul_num}"
        elif mk_clean or nim or nama or modul_num:
            parts = []
            if mk_clean:
                parts.append(f"Prak{mk_clean}")
            if nim:
                parts.append(nim)
            if nama:
                parts.append(nama)
            if modul_num:
                parts.append(f"Modul{modul_num}")
            judul_laporan = "_".join(parts) if len(parts) >= 2 else cls.DEFAULT_JUDUL_LAPORAN
        else:
            judul_laporan = cls.DEFAULT_JUDUL_LAPORAN

        if modul_num and mk:
            materi_modul = f"Modul {modul_num} Prak. {mk}"
            if judul_modul:
                materi_modul += f" - {judul_modul}"
        elif modul_path:
            base = os.path.splitext(os.path.basename(modul_path))[0].strip()
            materi_modul = base or cls.DEFAULT_MATERI_MODUL
        elif mk:
            materi_modul = f"Prak. {mk}"
        else:
            materi_modul = cls.DEFAULT_MATERI_MODUL

        return judul_laporan, materi_modul

    @staticmethod
    def instruksi_gaya():
        """Aturan gaya akademis anti-slop untuk backward compatibility."""
        return (
            "\n"
            "ATURAN WAJIB (JANGAN DILANGGAR):\n"
            "1. LANGSUNG KE INTI. DILARANG KERAS menggunakan kalimat pembuka seperti "
            "\"Berikut adalah analisa...\", \"Berdasarkan gambar...\", \"Analisa:\", atau \"Pada bab ini...\".\n"
            "2. Mulailah langsung dengan kata pertama dari paragraf 1.\n"
            "3. Buat TEPAT 2 PARAGRAF. Masing-masing paragraf terdiri dari 3 hingga 5 kalimat singkat yang jelas dan padat.\n"
            "4. Fokuskan analisa pada aspek teknis dan teoritis yang relevan dengan modul.\n"
            "5. HINDARI penggunaan kata \"anda\", \"kamu\", \"kalian\", atau \"kita\". Gunakan gaya bahasa objektif akademis.\n"
            "6. JANGAN gunakan tanda kutip satu (') atau backtick (`) pada istilah teknis.\n"
            "7. Pisahkan antar paragraf dengan SATU KALI ENTER saja.\n"
        )

    @classmethod
    def build_analisa_prompt(
        cls,
        pilih_tipe,
        isi_a,
        judul_sub="Sub-Bab",
        judul_laporan="",
        materi_modul="",
        modul_excerpt="",
        has_image=False,
        instruksi=None,
    ):
        """Membangun prompt analisa sesuai instruksi pengguna & standar bebas AI Slop."""
        judul_laporan = judul_laporan or cls.DEFAULT_JUDUL_LAPORAN
        materi_modul = materi_modul or cls.DEFAULT_MATERI_MODUL
        judul_sub = judul_sub or "Sub-Bab Analisa"

        content_header = "KODE PROGRAM:"
        if str(pilih_tipe) == "2":
            content_header = "LANGKAH KERJA & DESKRIPSI:"
        elif str(pilih_tipe) == "3":
            content_header = "DAFTAR TANYA-JAWAB (Q&A):"

        modul_section = ""
        if modul_excerpt and modul_excerpt.strip():
            modul_section = f"\nBAHAN MATERI ACUAN ({materi_modul}):\n{modul_excerpt.strip()}\n"

        image_instruction = ""
        if has_image:
            image_instruction = (
                "\nLihat gambar output/tangkapan layar yang dilampirkan, lalu "
                "hubungkan temuan visual tersebut dengan penjelasan teknisnya."
            )

        prompt = (
            f"Buatkan draft analisa dan penjelasan untuk masing-masing sub bab analisa yang terdapat dalam laporan \"{judul_laporan}\". "
            f"Gunakan \"{materi_modul}\" sebagai bahan materi. "
            "Pastikan untuk menghindari penulisan bab yang merujuk pada pembahasan praktikum dan juga hindari penggunaan kata \"anda\" dalam penulisan draf ini. "
            "Setiap draf analisa atau penjelasan harus terdiri dari 2 paragraf, dengan masing-masing paragraf terdiri dari 3 hingga 5 kalimat singkat yang jelas dan padat. "
            "Fokuskan analisa pada aspek teknis dan teoritis yang relevan dengan modul.\n\n"
            f"TOPIK SUB-BAB: \"{judul_sub}\"\n"
            f"{modul_section}\n"
            f"{content_header}\n{isi_a}\n"
            f"{image_instruction}\n\n"
            "PEDOMAN STRUKTUR & LARANGAN WAJIB (HUMAN-WRITTEN ACADEMIC STYLE):\n"
            "1. Tulis TEPAT 2 PARAGRAF.\n"
            "2. Setiap paragraf WAJIB terdiri dari 3 sampai 5 kalimat singkat yang padat, akurat, dan teknis.\n"
            "3. HINDARI penyebutan nama bab atau pembahasan praktikum (DILARANG: \"Pada bab ini\", \"Pada sub-bab ini\", \"Dalam praktikum ini\", \"Praktikum ini membahas\", \"Berikut adalah analisa\").\n"
            "4. HINDARI penggunaan kata \"anda\", \"kamu\", \"kalian\", atau \"kita\". Gunakan kalimat objektif ilmiah.\n"
            "5. HINDARI pembuka dan transisi klise AI (DILARANG: \"Secara keseluruhan\", \"Penting untuk dipahami bahwa\", \"Sebagai kesimpulan\", \"Tentunya\").\n"
            "6. JANGAN gunakan tanda kutip satu (') atau backtick (`) pada istilah teknis.\n"
            "7. Paragraf 1 membedah logika teknis, arsitektur kode/perintah, alur eksekusi, atau metodologi.\n"
            "8. Paragraf 2 membedah landasan teori, analisis hasil/output, serta relevansi sistem terhadap konsep modul.\n"
            "9. Langsung mulai dari kata pertama paragraf 1 tanpa judul atau basa-basi pengantar.\n"
            "10. Pisahkan paragraf 1 dan paragraf 2 HANYA dengan SATU KALI ENTER (baris baru).\n"
        )
        return prompt.strip()

    @classmethod
    def build_kesimpulan_prompt(
        cls,
        bab1_text,
        bab2_text,
        judul_laporan="",
        materi_modul="",
        modul_excerpt="",
    ):
        """Membangun prompt kesimpulan sesuai instruksi pengguna & standar bebas AI Slop."""
        judul_laporan = judul_laporan or cls.DEFAULT_JUDUL_LAPORAN
        materi_modul = materi_modul or cls.DEFAULT_MATERI_MODUL

        modul_section = ""
        if modul_excerpt and modul_excerpt.strip():
            modul_section = f"\nBAHAN MATERI ACUAN ({materi_modul}):\n{modul_excerpt.strip()}\n"

        prompt = (
            f"Buatkan draf kesimpulan sebanyak 3 paragraf mengenai \"{materi_modul}\". "
            "Setiap paragraf harus terdiri dari 3-5 kalimat singkat. "
            "Paragraf pertama harus diawali dengan kalimat \"Pada praktikum kali ini, ...\". "
            f"Draft tersebut akan disimpan dalam Bab Kesimpulan pada laporan berjudul \"{judul_laporan}\". "
            "Dalam penulisan draf ini, hindari penggunaan kata \"anda\". "
            "Pastikan setiap paragraf menyajikan pemikiran yang ringkas dan jelas.\n\n"
            f"{modul_section}\n"
            f"RINGKASAN HASIL PRAKTIKUM (BAB 1):\n{bab1_text}\n\n"
            f"RINGKASAN TUGAS (BAB 2):\n{bab2_text}\n\n"
            "PEDOMAN STRUKTUR & LARANGAN WAJIB (HUMAN-WRITTEN STYLE):\n"
            "1. Tulis TEPAT 3 PARAGRAF.\n"
            "2. Setiap paragraf WAJIB terdiri dari 3 hingga 5 kalimat singkat yang padat dan bermakna.\n"
            "3. Paragraf 1 WAJIB DIAWALI dengan kalimat: \"Pada praktikum kali ini, ...\"\n"
            "4. Paragraf 1 memaparkan tujuan praktikum dan intisari implementasi teknis yang diselesaikan.\n"
            "5. Paragraf 2 memaparkan evaluasi temuan teknis, validasi teori berdasarkan hasil percobaan, dan fungsi komponen utama.\n"
            "6. Paragraf 3 memaparkan kesimpulan menyeluruh, efektivitas metode yang dipelajari, serta pemahaman esensial praktikan.\n"
            "7. HINDARI penggunaan kata \"anda\", \"kamu\", \"kalian\", atau \"kita\".\n"
            "8. HINDARI transisi atau kalimat basi AI (DILARANG: \"Secara keseluruhan\", \"Dapat disimpulkan bahwa\", \"Sebagai penutup\", \"Penting untuk diingat bahwa\", \"Tentunya\").\n"
            "9. JANGAN gunakan tanda kutip satu (') atau backtick (`) pada istilah teknis.\n"
            "10. Pisahkan antar paragraf HANYA dengan SATU KALI ENTER (baris baru).\n"
        )
        return prompt.strip()

    @classmethod
    def build_langkah_kerja_prompt(
        cls,
        judul_sub,
        judul_laporan="",
        materi_modul="",
        modul_excerpt="",
        has_image=False,
        image_context="",
    ):
        """Membangun prompt langkah kerja bergaya manusia (human student notes)."""
        judul_laporan = judul_laporan or cls.DEFAULT_JUDUL_LAPORAN
        materi_modul = materi_modul or cls.DEFAULT_MATERI_MODUL

        context_lines = []
        if modul_excerpt and modul_excerpt.strip():
            context_lines.append(f"Konteks Modul ({materi_modul}):\n{modul_excerpt.strip()}")
        if image_context and image_context.strip():
            context_lines.append(f"Deskripsi Tambahan:\n{image_context.strip()}")
        if has_image:
            context_lines.append("Gunakan screenshot yang dilampirkan sebagai rujukan antarmuka / hasil eksekusi program.")

        context_str = ("\n\n" + "\n\n".join(context_lines)) if context_lines else ""

        prompt = (
            "Peran: Mahasiswa praktikan lab komputer yang mencatat langkah kerja secara teknis, ringkas, dan mandiri.\n"
            f"Tugas: Susun langkah kerja praktikum untuk sub-bab \"{judul_sub}\" pada laporan \"{judul_laporan}\" mengacu pada \"{materi_modul}\".{context_str}\n\n"
            "PEDOMAN WAJIB (HUMAN-WRITTEN PRACTICAL NOTES, BEBAS AI SLOP):\n"
            "1. Kuantitas: Tulis antara 7 hingga 12 baris langkah kerja teknis.\n"
            "2. Format: Tulis satu tindakan konkret per baris TANPA penomoran (1. 2. 3.) dan TANPA bullet (*, -, •). Penomoran dibuat otomatis oleh sistem.\n"
            "3. Gaya Bahasa Manusia: Gunakan kalimat imperatif/tindakan aktif langsung yang alami (contoh: \"Buka terminal lalu install pustaka pendukung...\", \"Import module os dan sys pada script utama...\", \"Jalankan file program dan amati keluaran sinyal...\").\n"
            "4. HINDARI bahasa robotik AI (DILARANG: \"Pengguna kemudian diarahkan untuk...\", \"Langkah berikutnya adalah memastikan bahwa...\", \"Hal ini bertujuan untuk...\", \"Pastikan Anda...\").\n"
            "5. DILARANG memasukkan langkah sampah non-teknis (DILARANG: \"Siapkan laptop\", \"Berdoa\", \"Nyalakan komputer\", \"Selesai\").\n"
            "6. HINDARI penggunaan kata \"anda\", \"kamu\", atau \"kita\".\n"
        )
        return prompt.strip()

    @classmethod
    def build_penjelasan_singkat_prompt(
        cls,
        judul_sub,
        judul_laporan="",
        materi_modul="",
        modul_excerpt="",
    ):
        """Membangun prompt penjelasan singkat sub-bab (tepat 2 paragraf, 3-5 kalimat per paragraf)."""
        judul_laporan = judul_laporan or cls.DEFAULT_JUDUL_LAPORAN
        materi_modul = materi_modul or cls.DEFAULT_MATERI_MODUL

        modul_section = ""
        if modul_excerpt and modul_excerpt.strip():
            modul_section = f"\nBAHAN MATERI ACUAN ({materi_modul}):\n{modul_excerpt.strip()}\n"

        prompt = (
            f"Buatkan draft analisa dan penjelasan untuk masing-masing sub bab analisa yang terdapat dalam laporan \"{judul_laporan}\". "
            f"Gunakan \"{materi_modul}\" sebagai bahan materi. "
            "Pastikan untuk menghindari penulisan bab yang merujuk pada pembahasan praktikum dan juga hindari penggunaan kata \"anda\" dalam penulisan draf ini. "
            "Setiap draf analisa atau penjelasan harus terdiri dari 2 paragraf, dengan masing-masing paragraf terdiri dari 3 hingga 5 kalimat singkat yang jelas dan padat. "
            "Fokuskan analisa pada aspek teknis dan teoritis yang relevan dengan modul.\n\n"
            f"TOPIK SUB-BAB: \"{judul_sub}\"\n"
            f"{modul_section}\n"
            "PEDOMAN STRUKTUR & LARANGAN WAJIB (HUMAN-WRITTEN STYLE):\n"
            "1. Tulis TEPAT 2 PARAGRAF.\n"
            "2. Masing-masing paragraf WAJIB terdiri dari 3 hingga 5 kalimat singkat yang jelas dan padat.\n"
            "3. Paragraf 1 membedah konsep dasar dan teori pendukung yang mendasari topik ini.\n"
            "4. Paragraf 2 membedah aspek teknis dan penerapannya dalam modul praktikum.\n"
            "5. HINDARI penulisan bab yang merujuk pada pembahasan praktikum (DILARANG: \"Pada bab ini\", \"Pada sub-bab ini\", \"Dalam praktikum ini\").\n"
            "6. HINDARI penggunaan kata \"anda\", \"kamu\", \"kalian\", atau \"kita\".\n"
            "7. HINDARI pembuka klise (DILARANG: \"Berikut adalah...\", \"Secara umum...\", \"Penting untuk dipahami bahwa...\").\n"
            "8. JANGAN gunakan tanda kutip satu (') atau backtick (`).\n"
            "9. Langsung mulai dari kata pertama tanpa kalimat pembuka tambahan.\n"
            "10. Pisahkan antar paragraf HANYA dengan SATU KALI ENTER (baris baru).\n"
        )
        return prompt.strip()

    @classmethod
    def build_prompt(cls, pilih_tipe, isi_a, instruksi):
        """Backward-compatible fallback caller."""
        return cls.build_analisa_prompt(
            pilih_tipe=pilih_tipe,
            isi_a=isi_a,
            judul_sub="Analisa Praktikum",
            instruksi=instruksi,
        )

    @staticmethod
    def sanitize_ai_output(text: str, is_kesimpulan: bool = False) -> str:
        """Membersihkan output AI dari artefak markdown, slop pembuka, dan kata ganti orang kedua."""
        if not text:
            return ""

        cleaned = text.strip()

        # Hapus markdown code block wrappers (``` atau ```text)
        if cleaned.startswith("```"):
            cleaned = re.sub(r"^```[a-zA-Z0-9_-]*\s*\n?", "", cleaned)
            cleaned = re.sub(r"\n?```\s*$", "", cleaned)
            cleaned = cleaned.strip()

        # Hapus tanda kutip satu dan backtick pada istilah
        cleaned = cleaned.replace("`", "")
        cleaned = re.sub(r"(?<=\s)'([A-Za-z0-9_.-]+)'(?=[\s.,!?;:])", r"\1", cleaned)

        # Hapus baris pembuka AI basa-basi
        cleaned = re.sub(
            r"^(?:Berikut (?:ini )?adalah\s+(?:draft\s+)?(?:analisa|penjelasan|kesimpulan)[^:\n]*:?\s*)",
            "",
            cleaned,
            flags=re.IGNORECASE,
        )
        cleaned = re.sub(
            r"^(?:Berdasarkan\s+(?:gambar|kode|hasil|output|screenshot)[^:\n]*:?\s*)",
            "",
            cleaned,
            flags=re.IGNORECASE,
        )
        cleaned = re.sub(
            r"^(?:Analisa|Kesimpulan|Penjelasan Singkat|Draft Analisa|Draf Kesimpulan):\s*",
            "",
            cleaned,
            flags=re.IGNORECASE,
        )

        paragraphs = [p.strip() for p in cleaned.split("\n") if p.strip()]
        cleaned_paras = []

        for p in paragraphs:
            # Hapus kata klise pembuka paragraf
            p = re.sub(
                r"^(?:Secara keseluruhan,?\s*|Dapat disimpulkan bahwa\s*|Penting untuk (?:diingat|dicatat|dipahami) bahwa\s*|Sebagai kesimpulan,?\s*|Perlu (?:diingat|diketahui) bahwa\s*)",
                "",
                p,
                flags=re.IGNORECASE,
            )
            # Hapus kata ganti orang kedua
            p = re.sub(r"\b[Aa]nda\b", "praktikan", p)
            p = re.sub(r"\b[Kk]amu\b", "praktikan", p)
            p = re.sub(r"\b[Kk]alian\b", "praktikan", p)
            # Ganti sapaan kita jika merujuk pembaca
            p = re.sub(r"\b[Kk]ita dapat melihat\b", "dapat diamati", p)
            p = re.sub(r"\b[Kk]ita dapat\b", "dapat", p)
            p = re.sub(r"\b[Kk]ita\b", "praktikan", p)
            # Hindari frasa merujuk ke bab dalam analisa
            if not is_kesimpulan:
                p = re.sub(r"\bPada bab ini,?\s*", "", p, flags=re.IGNORECASE)
                p = re.sub(r"\bPada sub-?bab ini,?\s*", "", p, flags=re.IGNORECASE)
                p = re.sub(r"\bDalam praktikum ini,?\s*", "Secara teknis, ", p, flags=re.IGNORECASE)

            p = p.strip()
            if p:
                p = p[0].upper() + p[1:]
                cleaned_paras.append(p)

        if not cleaned_paras:
            return ""

        if is_kesimpulan and cleaned_paras:
            p1 = cleaned_paras[0]
            req_prefix = "Pada praktikum kali ini, "
            if p1.lower().startswith("pada praktikum kali ini,"):
                cleaned_paras[0] = req_prefix + p1[len("pada praktikum kali ini,"):].strip()
            elif p1.lower().startswith("praktikum kali ini,"):
                cleaned_paras[0] = req_prefix + p1[len("praktikum kali ini,"):].strip()
            elif p1.lower().startswith("pada praktikum ini,"):
                cleaned_paras[0] = req_prefix + p1[len("pada praktikum ini,"):].strip()
            else:
                first_word = p1.split()[0] if p1.split() else ""
                if first_word.isupper() or first_word.startswith("(") or first_word in ["MATLAB", "Python", "Praat", "FFT", "MFCC"]:
                    cleaned_paras[0] = req_prefix + p1
                else:
                    cleaned_paras[0] = req_prefix + p1[0].lower() + p1[1:]

        return "\n\n".join(cleaned_paras)
