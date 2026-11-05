# Praktikum AI Agent Pertemuan 03

## Isi

- attention_demo.py: tokenisasi sederhana, embedding ilustratif, Q-K-V, self-attention, causal mask.
- mini_agent.py: simulasi coding agent yang mencari, membaca, mengedit file, dan menjalankan tes.
- sample_project/: program akademik yang sengaja memiliki bug dan unit test.

## Syarat

Python 3.9+ (disarankan 3.10+). Tidak memerlukan GPU, internet, API key, NumPy, atau paket tambahan.

## Menjalankan

1. Periksa Python: `python --version` (Windows dapat memakai `py --version`).
2. Dari folder utama jalankan `python attention_demo.py`.
3. Masuk ke folder tes: `cd sample_project`.
4. Jalankan tes awal: `python -m unittest discover -s tests -v`. Satu tes nilai E diharapkan gagal dengan KeyError: 'E'.
5. Kembali ke folder utama: `cd ..`.
6. Jalankan `python mini_agent.py`. Agent mencari fungsi, membaca file, menjalankan tes, menambah bobot E=0.0, lalu tes ulang.
7. Verifikasi lagi: `cd sample_project`, lalu `python -m unittest discover -s tests -v`. Semua tes seharusnya lulus.

Pada Windows jika `python` tidak dikenali, coba `py`. Pada macOS/Linux, jika perlu gunakan `python3`.

## Batasan akademik

Tokenisasi memakai `split()`, bukan BPE. Embedding hanya angka ilustratif. Mini agent memakai aturan deterministik, bukan LLM Transformer terlatih. Program ini mendemonstrasikan loop agen dan pemanggilan tools, bukan membuat model bahasa dari nol.

## Tantangan

1. Tambahkan nilai F berbobot 0.0 dan unit test.
2. Tambahkan validasi nilai yang tidak dikenal.
3. Tambahkan tool list_files.
4. Tambahkan logging tool call dan observation.
5. Rancang konfirmasi manusia untuk operasi berisiko.

## Pertanyaan Analisis dan Jawaban (Modul Praktikum Bagian N)

### 1. Mengapa ID token perlu diubah menjadi embedding?
* **Keterbatasan ID Token:** Tokenizer mengubah teks menjadi potongan token dan memberinya ID berupa bilangan bulat (*integer*). Namun, ID ini bersifat diskrit, kategorikal, dan arbitrer. ID tidak memiliki makna semantik maupun jarak geometris (misalnya ID 100 tidak berarti memiliki nilai dua kali lipat atau memiliki kedekatan makna dengan ID 50).
* **Peran Embedding:** Matriks *embedding* ($E \in \mathbb{R}^{|V| \times d}$) memetakan setiap ID token menjadi vektor numerik kontinu dalam ruang berdimensi tinggi ($d$).
* **Manfaat:**
  1. Kata-kata dengan makna serupa atau konteks penggunaan yang mirip akan berada berdekatan dalam ruang vektor (dapat diukur dengan *cosine similarity*).
  2. Hubungan semantik antarkata dapat direpresentasikan sebagai pergeseran arah vektor (misal: $\vec{v}_{\text{raja}} - \vec{v}_{\text{pria}} + \vec{v}_{\text{wanita}} \approx \vec{v}_{\text{ratu}}$).
  3. Bobot vektor embedding dapat diperbarui dan dioptimalkan bersama parameter model lainnya melalui *backpropagation*.

---

### 2. Apa perbedaan Query, Key, dan Value?
Dalam mekanisme *Scaled Dot-Product Attention*:
* **Query ($Q$):** Vektor yang merepresentasikan **apa yang sedang dicari** oleh token saat ini (*"Informasi apa yang saya butuhkan dari token lain?"*).
* **Key ($K$):** Vektor yang merepresentasikan **label atau identitas fitur** yang dimiliki token untuk dicocokkan dengan Query (*"Saya token tentang apa / apa kata kunci saya?"*).
* **Value ($V$):** Vektor yang merepresentasikan **konten informasi aktual** yang akan disumbangkan (*weighted sum*) jika Key-nya cocok dengan Query.
* **Analogi Perpustakaan / YouTube:**
  * **Query:** Kata kunci yang Anda ketik di kolom pencarian.
  * **Key:** Judul, tag, atau indeks buku/video yang dicocokkan dengan kata kunci.
  * **Value:** Isi konten buku atau video yang Anda dapatkan berdasarkan hasil pencocokan.

---

### 3. Mengapa causal mask membuat bobot token masa depan menjadi nol?
* **Tujuan Autoregresif:** Model *decoder-only* (seperti GPT, Claude, Gemini) dilatih untuk memprediksi token berikutnya ($x_t$) hanya berdasarkan token-token masa lalu ($x_{<t}$). Jika model diizinkan melihat token masa depan saat pelatihan atau inferensi, model akan "menyontek" dan tidak belajar memprediksi secara kausal.
* **Mekanisme Matematis:** *Causal mask* mengganti nilai skor *attention* ($QK^T / \sqrt{d_k}$) untuk token-token masa depan dengan nilai $-\infty$ (negatif tak hingga) sebelum masuk ke fungsi *softmax*.
* **Hasil Softmax:** Fungsi *softmax* menghitung bobot melalui eksponensial:
  $$w_i = \frac{e^{z_i}}{\sum_j e^{z_j}}$$
  Karena $e^{-\infty} = 0$, probabilitas bobot perhatian untuk seluruh token masa depan menjadi **tepat 0**.

---

### 4. Mengapa output tool dimasukkan kembali ke konteks?
* **Transformer Bersifat Stateless:** Model Transformer tidak memiliki memori internal yang bertahan antar-*forward pass*. Setiap pemanggilan API/model dilakukan dari nol.
* **Umpan Balik Tindakan (*Feedback Loop*):** Agar model "mengetahui" apa yang baru saja terjadi di lingkungan nyata (misalnya isi file yang dibaca, traceback error, atau hasil tes), output eksekusi (*Observation*) harus ditambahkan ke dalam daftar percakapan (*context window*).
* **Penalaran Langkah Berikutnya:** Dengan adanya observasi di konteks, mekanisme *self-attention* pada langkah iterasi berikutnya dapat menghubungkan instruksi tugas dengan hasil tool sebelumnya untuk memutuskan tindakan lanjutan (apakah mengedit file, mencoba tool lain, atau menyimpulkan jawaban akhir).

---

### 5. Apa perbedaan Transformer/LLM dengan runtime?
* **Transformer / LLM ("Otak"):**
  * Model komputasi jaringan saraf yang bertugas memproses token konteks dan memprediksi token berikutnya (teks penjelasan, penalaran, atau string JSON pemanggilan tool).
  * **Tidak memiliki akses fisik** ke sistem operasi, filesystem, atau terminal. LLM tidak bisa menjalankan kode sendiri.
* **Runtime ("Tangan / Eksekutor"):**
  * Perangkat lunak lingkungan eksekusi (seperti Python interpreter, shell OS, atau container sandbox).
  * Runtime membaca teks JSON yang dihasilkan LLM, memvalidasi keamanan, mengeksekusi instruksi fisik di komputer (membaca file, menjalankan unit test via `subprocess`), lalu mengembalikan outputnya ke konteks LLM sebagai observasi.

---

### 6. Mengapa unit test lebih kuat daripada klaim agen bahwa perbaikan benar?
* **Masalah Halusinasi dan Overconfidence:** LLM bersifat probabilistik. Agen bisa saja secara meyakinkan menghasilkan teks penjelasan bahwa "kode telah diperbaiki dan bug selesai", padahal masih terdapat kesalahan sintaksis, *regression bug*, atau kasus batas (*edge case*) yang belum tertangani.
* **Unit Test sebagai Oracle Eksternal:** Unit test dieksekusi secara nyata dan deterministik oleh runtime independen. Tes menguji perilaku fungsional kode terhadap kriteria input-output yang baku.
* **Bukti Empiris:** Keberhasilan unit test adalah bukti empiris objektif bahwa kode benar-benar berfungsi, bukan sekadar prediksi teks dari model bahasa.

---

### 7. Apa kekurangan mini coding agent dibandingkan agen berbasis LLM?
* **Deterministik & Kaku (*Hardcoded Rules*):** Mini coding agent pada praktikum ini menggunakan aturan berbasis kondisi statis (`if-else`, string matching tetap seperti `def hitung_ipk`, dan string replacement sederhana). Jika nama file berubah, nama fungsi berbeda, atau tipe bug bukan `KeyError`, mini agent akan langsung gagal.
* **Tidak Memiliki Pemahaman Semantik:** Mini agent tidak dapat membaca dan menganalisis pesan error secara fleksibel, melainkan hanya memeriksa apakah exit code bernilai 0 atau tidak.
* **Tidak Adaptif:** Agen tidak dapat merancang strategi perbaikan alternatif jika solusi pertama gagal (tidak memiliki kemampuan *Tree of Thoughts* atau *Reflexion*). Sebaliknya, agen berbasis LLM memiliki fleksibilitas penalaran bahasa alami untuk membedah kode kompleks apa pun secara dinamis.

---

## Latihan dan Diskusi Tambahan (Bahan Presentasi Hal. 34)

### A. Perhitungan Manual Attention Baris "suka"
Diberikan: $d_k = 2 \implies \sqrt{d_k} = \sqrt{2} \approx 1.4142$
* $Q_{\text{suka}} = [1, 1]$
* $K = [\text{saya: } [1, 1],\ \text{suka: } [0, 1],\ \text{kopi: } [1, 2]]$
* $V = [\text{saya: } [0, 1],\ \text{suka: } [1, 0],\ \text{kopi: } [1, 1]]$

1. **Skor Dot-Product ($Q \cdot K^T / \sqrt{2}$):**
   * $\text{kolega saya}: (1\times 1 + 1\times 1)/\sqrt{2} = 2 / 1.4142 \approx 1.4142$
   * $\text{kolega suka}: (1\times 0 + 1\times 1)/\sqrt{2} = 1 / 1.4142 \approx 0.7071$
   * $\text{kolega kopi}: (1\times 1 + 1\times 2)/\sqrt{2} = 3 / 1.4142 \approx 2.1213$
   * **Skor:** $[1.4142,\ 0.7071,\ 2.1213]$

2. **Tanpa Mask:**
   * Softmax: $e^{1.4142} \approx 4.1132$, $e^{0.7071} \approx 2.0281$, $e^{2.1213} \approx 8.3420$ (Total $\approx 14.4833$)
   * **Bobot:** $[0.2840,\ 0.1400,\ 0.5760] \approx [0.28,\ 0.14,\ 0.58]$
   * **Output $Z$:** $0.28[0, 1] + 0.14[1, 0] + 0.58[1, 1] \approx [0.72,\ 0.86]$

3. **Dengan Causal Mask (`mask = [True, True, False]`):**
   * Skor: $[1.4142,\ 0.7071,\ -\infty]$
   * Softmax: $e^{1.4142} \approx 4.1132$, $e^{0.7071} \approx 2.0281$, $e^{-\infty} = 0$ (Total $\approx 6.1413$)
   * **Bobot Masked:** $[0.6698,\ 0.3302,\ 0.0] \approx [0.67,\ 0.33,\ 0.0]$
   * **Output $Z_{\text{masked}}$:** $0.67[0, 1] + 0.33[1, 0] + 0[1, 1] \approx [0.33,\ 0.67]$

---

### B. Trace ReAct: Validasi NIM 10 Digit pada Form Pendaftaran
* **[USER]:** Tambahkan validasi NIM 10 digit pada form pendaftaran.
* **[THOUGHT 1]:** Saya perlu mencari letak fungsi validasi form pendaftaran di repositori.
* **[ACTION 1]:** `grep("def validate_nim")`
* **[OBSERVATION 1]:** `src/validators.py:10: def validate_nim(nim):`
* **[THOUGHT 2]:** Saya harus membaca implementasi fungsi saat ini.
* **[ACTION 2]:** `read_file("src/validators.py")`
* **[OBSERVATION 2]:** `def validate_nim(nim): return True` (belum ada pengecekan digit dan panjang).
* **[THOUGHT 3]:** Perbarui fungsi agar memvalidasi bahwa input berupa string angka dengan panjang 10 digit.
* **[ACTION 3]:** `edit_file("src/validators.py", old="return True", new="return isinstance(nim, str) and len(nim) == 10 and nim.isdigit()")`
* **[OBSERVATION 3]:** Berhasil: perubahan diterapkan.
* **[THOUGHT 4]:** Jalankan test suite untuk memverifikasi fungsionalitas validasi baru.
* **[ACTION 4]:** `run_shell("pytest tests/test_validators.py")`
* **[OBSERVATION 4]:** `4 passed in 0.03s`
* **[FINAL ANSWER]:** Validasi NIM 10 digit numerik telah berhasil ditambahkan pada `src/validators.py` dan seluruh unit test lulus.

---

### C. Pertanyaan Refleksi & Diskusi
1. **Di mana ingatan agen berada jika Transformer stateless?**
   * *Ingatan jangka pendek:* Disimpan di dalam **Context Window** (riwayat percakapan dan observasi yang dikirimkan ulang pada setiap langkah iterasi).
   * *Ingatan jangka panjang:* Disimpan di luar model (seperti basis data vektor / Vector DB, file log, atau dokumen eksternal) yang dipanggil ke dalam konteks saat dibutuhkan menggunakan teknik Retrieval-Augmented Generation (RAG).
2. **Mengapa prompt injection sulit dicegah hanya pada tingkat model?**
   * Karena bagi arsitektur Transformer, semua input (baik system prompt pengembang maupun input eksternal dari pengguna yang tidak tepercaya) digabungkan menjadi aliran token teks yang sama. Model memproses semua token menggunakan mekanisme attention yang sama tanpa pembatas fisik bawaan antara "instruksi sistem" dan "data pengguna".
3. **Kapan agen coding harus meminta persetujuan manusia (*human-in-the-loop*)?**
   * Saat akan melakukan operasi berisiko tinggi (*high-risk/destructive actions*), seperti: menghapus file/database (`rm -rf`, `DROP TABLE`), melakukan commit/push langsung ke branch produksi, memodifikasi kredensial/kunci API, atau menjalankan perintah shell yang mengakses jaringan luar/mengubah konfigurasi sistem OS host.
