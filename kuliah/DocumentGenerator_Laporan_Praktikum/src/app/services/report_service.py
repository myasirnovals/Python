import os

from docxtpl import DocxTemplate

from app.doc_helpers import muat_gambar


class ReportService:
    def __init__(self, templates_dir):
        self.templates_dir = templates_dir

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
            label_a = "Source Code" if item.get("tipe") == "1" else "Langkah Kerja"
            isi_a = item.get("isi_a", "") if item.get("tipe") == "2" else ""

            kode_items = item.get("kode_files", [])
            list_kode_final = []
            if len(kode_items) > 0:
                for i, d in enumerate(kode_items, 1):
                    judul_tampil = f"{i}. {d['nama']}" if len(kode_items) > 1 else ""
                    list_kode_final.append({"judul": judul_tampil, "isi": d.get("isi", "")})

            list_gbr = []
            for g in item.get("gambar_paths", []):
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
                    "list_gambar": list_gbr,
                    "isi_analisa": item.get("analisa", ""),
                    "list_kode": list_kode_final,
                }
            )

        return daftar_sub_bab

    def build_bab2_context(self, doc, bab2_items):
        daftar_tugas = []
        counter_gbr_bab2 = 1
        for item in bab2_items:
            list_gbr_tgs = []
            for g in item.get("gambar_paths", []):
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

            daftar_tugas.append(
                {
                    "judul_sub_bab": item.get("judul_sub_bab", ""),
                    "isi_soal": item.get("isi_soal", ""),
                    "isi_jawaban": item.get("isi_jawaban", ""),
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
