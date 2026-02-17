import os
import re

try:
    import win32com.client as win32
except Exception:  # pragma: no cover - optional dependency
    win32 = None
from docx import Document
from docxtpl import DocxTemplate, RichText

from app.doc_helpers import muat_gambar


class ReportService:
    def __init__(self, templates_dir):
        self.templates_dir = templates_dir

    @staticmethod
    def _normalize_langkah_list(raw_value):
        if not raw_value:
            return []

        # Jika sudah dalam bentuk list of dict (dari UI), langsung return
        if isinstance(raw_value, list) and len(raw_value) > 0 and isinstance(raw_value[0], dict):
            return raw_value

        if isinstance(raw_value, str):
            lines = [line.strip() for line in raw_value.split("\n") if line.strip()]
        else:
            lines = raw_value

        normalized = []
        for idx, line in enumerate(lines, 1):
            if not isinstance(line, str): continue
            
            # Bersihkan karakter sampah di awal (sama seperti di UI)
            text = re.sub(r'^[^\w\s\d]+', '', line).strip()
            
            # Regex yang lebih fleksibel
            match = re.match(r'^\s*(\d+)[\s\.\)\-]*\s*(.*)', text)
            
            if match:
                nomor = match.group(1)
                langkah = match.group(2).strip()
            else:
                nomor = idx
                langkah = text

            normalized.append({"nomor": nomor, "langkah_kerja": langkah})

        return normalized

    def resolve_template(self, template_choice):
        name = "format-1.docx" if template_choice == "1" else "format-2.docx"
        template_path = os.path.join(self.templates_dir, name)
        if not os.path.exists(template_path):
            raise FileNotFoundError(template_path)
        return template_path

    def build_bab1_context(self, doc, bab1_items):
        daftar_sub_bab = []
        counter_gbr_bab1 = 1
        for item in bab1_items:
            label_a = item.get("label_point_a") or (
                "Source Code" if item.get("tipe") == "1" else "Langkah Kerja"
            )
            langkah_list = self._normalize_langkah_list(
                item.get("langkah_list") or item.get("isi_a", "")
            )
            if item.get("tipe") == "2":
                isi_a = "\n".join(
                    [step.get("langkah_kerja", "") for step in langkah_list]
                )
            else:
                isi_a = ""

            kode_items = item.get("list_kode") or item.get("kode_files", [])
            list_kode_final = []
            if len(kode_items) > 0:
                for i, d in enumerate(kode_items, 1):
                    nama_tampil = d.get("judul") or d.get("nama", "")
                    if len(kode_items) > 1:
                        prefix = "\n" if i > 1 else ""
                        judul_tampil = RichText(f"{prefix}{i}. {nama_tampil}")
                    else:
                        judul_tampil = "##HAPUS##"
                    list_kode_final.append(
                        {"judul": judul_tampil, "isi": d.get("isi", "")}
                    )

            list_gbr = []
            for g in item.get("list_gambar") or item.get("gambar_paths", []):
                obj = muat_gambar(doc, g.get("path", ""))
                if not obj:
                    continue
                list_gbr.append(
                    {
                        "objek_gambar": obj,
                        "caption": g.get("caption", ""),
                        "nomor_tampil": counter_gbr_bab1,
                    }
                )
                counter_gbr_bab1 += 1

            daftar_sub_bab.append(
                {
                    "judul_sub_bab": item.get("judul_sub_bab", ""),
                    "label_point_a": label_a,
                    "isi_point_a": isi_a,
                    "langkah_list": langkah_list,
                    "list_gambar": list_gbr,
                    "isi_analisa": item.get("isi_analisa") or item.get("analisa", ""),
                    "list_kode": list_kode_final,
                }
            )

        return daftar_sub_bab

    @staticmethod
    def _hapus_baris_hantu(nama_file):
        print("🧹 Membersihkan baris kosong...")
        try:
            doc_bersih = Document(nama_file)
            for p in list(doc_bersih.paragraphs):
                if "##HAPUS##" in p.text:
                    p._element.getparent().remove(p._element)
                    print("   ✨ Satu baris judul kosong berhasil dihapus.")
            doc_bersih.save(nama_file)
        except Exception as e:
            print(f"⚠️ Gagal membersihkan: {e}")

    @staticmethod
    def _update_toc_word(nama_file):
        print("      ⏳ Sedang melakukan Auto-Update Daftar Isi & Gambar...")
        if win32 is None:
            print("      ⚠️ Win32COM tidak tersedia. Lewati update TOC otomatis.")
            return
        try:
            path_lengkap = os.path.abspath(nama_file)
            word_app = win32.Dispatch("Word.Application")
            word_app.Visible = False
            word_app.DisplayAlerts = False

            doc = word_app.Documents.Open(path_lengkap)
            for toc in doc.TablesOfContents:
                toc.Update()
            doc.Fields.Update()
            doc.Save()
            doc.Close()
            word_app.Quit()
            print("      ✅ Auto-Update Selesai! Dokumen siap cetak.")
        except Exception as e:
            print(
                "      ⚠️ Gagal Auto-Update (Buka file manual lalu tekan Ctrl+A -> F9): "
                f"{e}"
            )

    def build_bab2_context(self, doc, bab2_items):
        daftar_tugas = []
        counter_gbr_bab2 = 1
        for item in bab2_items:
            tipe = item.get("tipe", "1")
            list_gbr_tgs = []
            for g in item.get("list_gambar") or item.get("gambar_paths", []):
                obj = muat_gambar(doc, g.get("path", ""))
                if not obj:
                    continue
                list_gbr_tgs.append(
                    {
                        "objek_gambar": obj,
                        "caption": g.get("caption", ""),
                        "nomor_tampil": counter_gbr_bab2,
                    }
                )
                counter_gbr_bab2 += 1

            list_kode_final = []
            if tipe == "1":
                kode_items = item.get("list_kode") or item.get("kode_files", [])
                if len(kode_items) > 0:
                    for i, d in enumerate(kode_items, 1):
                        nama_tampil = d.get("judul") or d.get("nama", "")
                        if len(kode_items) > 1:
                            prefix = "\n" if i > 1 else ""
                            judul_tampil = RichText(f"{prefix}{i}. {nama_tampil}")
                        else:
                            judul_tampil = "##HAPUS##"
                        list_kode_final.append(
                            {"judul": judul_tampil, "isi": d.get("isi", "")}
                        )

            qa_list = item.get("qa_list", [])
            qa_questions = []
            qa_answers = []
            for i, qa in enumerate(qa_list, 1):
                q_text = (qa.get("q") or "").strip()
                a_text = (qa.get("a") or "").strip()
                if q_text:
                    qa_questions.append(f"{i}. {q_text}")
                if a_text:
                    qa_answers.append(f"{i}. {a_text}")

            langkah_list = item.get("langkah_list", [])
            if not langkah_list and item.get("isi_a"):
                langkah_list = [
                    line.strip()
                    for line in item.get("isi_a", "").split("\n")
                    if line.strip()
                ]

            isi_a = item.get("isi_point_a") or item.get("isi_a", "")
            analisa = item.get("isi_analisa") or item.get("analisa", "")
            if not langkah_list:
                langkah_list = self._normalize_langkah_list(item.get("isi_a", ""))
            if tipe == "3":
                isi_soal = "\n".join(qa_questions)
                isi_jawaban = "\n".join(qa_answers)
                label_point_a = "Pertanyaan & Jawaban"
                isi_point_a = "\n".join(qa_questions)
                isi_analisa = ""
            elif tipe == "2":
                isi_soal = isi_a
                isi_jawaban = analisa
                label_point_a = "Langkah Kerja"
                isi_point_a = isi_a
                isi_analisa = analisa
            else:
                isi_soal = ""
                isi_jawaban = analisa
                label_point_a = "Source Code"
                isi_point_a = ""
                isi_analisa = analisa

            daftar_tugas.append(
                {
                    "judul_sub_bab": item.get("judul_sub_bab", ""),
                    "tipe": tipe,
                    "label_point_a": label_point_a,
                    "isi_point_a": isi_point_a,
                    "list_kode": list_kode_final,
                    "isi_analisa": isi_analisa,
                    "langkah_list": langkah_list,
                    "qa_list": qa_list,
                    "isi_soal": isi_soal,
                    "isi_jawaban": isi_jawaban,
                    "ada_gambar": len(list_gbr_tgs) > 0,
                    "list_gambar": list_gbr_tgs,
                }
            )

        return daftar_tugas

    def render_report(
        self, template_choice, cover, bab1_items, bab2_items, kesimpulan, output_path
    ):
        template_path = self.resolve_template(template_choice)
        doc = DocxTemplate(template_path)
        daftar_sub_bab = self.build_bab1_context(doc, bab1_items)
        daftar_tugas = self.build_bab2_context(doc, bab2_items)

        context = {
            **cover,
            "daftar_sub_bab": daftar_sub_bab,
            "daftar_tugas": daftar_tugas,
            "isi_kesimpulan": kesimpulan,
        }

        doc.render(context)
        doc.save(output_path)

        self._hapus_baris_hantu(output_path)
        self._update_toc_word(output_path)
