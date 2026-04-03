class PromptBuilder:
    """Build and centralize prompt templates used by AI workflows."""

    @staticmethod
    def instruksi_gaya():
        return (
            "\n"
            "            ATURAN WAJIB (JANGAN DILANGGAR):\n"
            "            1. LANGSUNG KE INTI. DILARANG KERAS menggunakan kalimat pembuka "
            "seperti \"Berikut adalah analisa...\", \"Berdasarkan gambar...\", "
            "atau \"Analisa:\".\n"
            "            2. Mulailah langsung dengan kata pertama dari paragraf 1.\n"
            "            3. Buat TEPAT 2 PARAGRAF.\n"
            "            4. Gunakan Bahasa Indonesia Formal yang akademis & padat (\"daging\").\n"
            "            5. JANGAN gunakan tanda kutip satu (') atau backtick (`) pada istilah teknis.\n"
            "            6. Pisahkan antar paragraf dengan SATU KALI ENTER saja.\n"
            "            "
        )

    @staticmethod
    def build_prompt(pilih_tipe, isi_a, instruksi):
        if pilih_tipe == "1":
            return (
                "\n                Analisa Laporan Praktikum Pemrograman.\n"
                "                KODE PROGRAM:\n"
                f"                {isi_a}\n\n"
                "                TUGAS:\n"
                "                Lihat gambar output yang dilampirkan, lalu jelaskan "
                "bagaimana kode di atas bekerja menghasilkan output tersebut.\n\n"
                f"                {instruksi}\n"
                "                "
            )

        if pilih_tipe == "3":
            return (
                "\n                Analisa Q and A Praktikum.\n\n"
                "                TUGAS:\n"
                "                Baca daftar pertanyaan dan jawaban di bawah, lalu jelaskan inti materi yang sedang dibahas secara ringkas dan formal.\n\n"
                f"                Daftar Q and A:\n                {isi_a}\n\n"
                f"                {instruksi}\n"
                "                "
            )

        return (
            "\n                Analisa Langkah Kerja Praktikum.\n\n"
            "                TUGAS:\n"
            "                Lihat screenshot yang dilampirkan. Jelaskan proses apa "
            "yang sedang dilakukan user di layar tersebut dan apa fungsi dari menu/tombol yang terlihat.\n\n"
            f"                Info Tambahan User: {isi_a}\n\n"
            f"                {instruksi}\n"
            "                "
        )
