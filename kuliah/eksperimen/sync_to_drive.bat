@echo off
echo ========================================================
echo  Sinkronisasi Eksperimen: H:\ ke Google Drive (J:\)
echo ========================================================
robocopy "H:\Documents\materi-pembelajaran\python\kuliah\eksperimen" "J:\My Drive\Data\perkuliahan\Penelitian\Pengumpulan Berkas\Proposal\Yasir Noval\eksperimen" /E /XD .git .ipynb_checkpoints checkpoints logs results
echo.
echo [*] Sinkronisasi selesai! File di Google Drive siap dijalankan di Colab.
pause
