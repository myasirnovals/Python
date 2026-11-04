# Kode Materi AI Agent — Pertemuan 02: Anatomi AI Agent

Paket ini mengikuti materi slide Pertemuan 02: loop agen, instruksi, tools, ReAct, tool calling, pola arsitektur, guardrails, dan evaluasi.

## Isi paket
- `demo_agen_akademik.py`: data dummy, tools akademik, agen rule-based, loop agen + tool calling versi offline, trace ReAct, evaluasi mini.
- `contoh_pola_arsitektur.py`: prompt chaining, routing, parallelization, orchestrator-workers, evaluator-optimizer.
- `latihan_mahasiswa.md`: lembar latihan dan pertanyaan refleksi.

## Menjalankan
Perlu Python 3.10+ direkomendasikan. Tidak perlu library tambahan, API key, atau internet.

```bash
python demo_agen_akademik.py
python contoh_pola_arsitektur.py
```

**Catatan penting:** `MockLLM` adalah simulasi heuristik offline, bukan model bahasa sungguhan. Ini digunakan agar mahasiswa dapat mengamati struktur tool calling tanpa API key. Semua jadwal, nilai, dan data mahasiswa adalah fiktif. Fungsi email hanya simulasi. Paket ini bahan ajar, bukan sistem akademik produksi.

## Kaitan dengan slide
- Anatomi dan loop runtime: `agen_llm()`
- Instruksi: `SYSTEM_PROMPT`
- Tools dan deskripsi tool: `TOOLS`, `TOOL_SCHEMAS`
- ReAct: `demo_react()`
- Rule-based vs LLM + tool calling: `AgenRuleBased` dibanding `agen_llm()`
- Guardrails: penolakan data massal, pemeriksaan tool, batas langkah, persetujuan aksi berisiko
- Evaluasi: `evaluasi()`
- Pola arsitektur: file `contoh_pola_arsitektur.py`
