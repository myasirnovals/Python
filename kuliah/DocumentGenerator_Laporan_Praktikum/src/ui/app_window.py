import os
import tkinter as tk
from tkinter import ttk

from app.ai_client import GeminiClient
from app.services.analysis_service import AnalysisService
from app.services.report_service import ReportService
from ui.bab1_tab import Bab1Tab
from ui.bab2_tab import Bab2Tab
from ui.bab3_tab import Bab3Tab
from ui.cover_tab import CoverTab
from ui.generate_tab import GenerateTab
from ui.styles import setup_styles

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
TEMPLATES_DIR = os.path.join(BASE_DIR, "..", "templates")


class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Lab Report Generator Pro")

        # --- UPDATE UKURAN (FINAL) ---
        # Lebar: 950
        # Tinggi: 630 (Naik dikit dari 600 biar ada napas di bawah)
        target_width = 950
        target_height = 630 

        screen_w = self.winfo_screenwidth()
        screen_h = self.winfo_screenheight()

        x_pos = (screen_w - target_width) // 2
        y_pos = (screen_h - target_height) // 2

        self.geometry(f"{target_width}x{target_height}+{x_pos}+{y_pos}")
        self.minsize(800, 550)
        # -----------------------------

        setup_styles(self)

        self.ai_client = GeminiClient()
        self.analysis_service = AnalysisService(self.ai_client)
        self.report_service = ReportService(TEMPLATES_DIR)

        self.cover_tab = None
        self.bab1_tab = None
        self.bab2_tab = None
        self.bab3_tab = None
        self.generate_tab = None

        self._build_ui()

    def _build_ui(self):
        self.configure(bg="#f8f9fa")

        # Padding 15 tetap, nanti akan terlihat pas dengan tinggi 630
        main_container = ttk.Frame(self)
        main_container.pack(fill="both", expand=True, padx=15, pady=15)

        header_frame = ttk.Frame(main_container)
        header_frame.pack(fill="x", pady=(0, 10))
        ttk.Label(header_frame, text="Lab Report Generator", style="Header.TLabel").pack(
            side="left"
        )
        ttk.Label(
            header_frame, text="v3.0.0 Beta", foreground="#6c757d"
        ).pack(side="left", padx=10, pady=(5, 0))

        self.notebook = ttk.Notebook(main_container)
        self.notebook.pack(fill="both", expand=True)

        cover_frame = ttk.Frame(self.notebook)
        bab1_frame = ttk.Frame(self.notebook)
        bab2_frame = ttk.Frame(self.notebook)
        bab3_frame = ttk.Frame(self.notebook)
        generate_frame = ttk.Frame(self.notebook)

        self.notebook.add(cover_frame, text="Cover")
        self.notebook.add(bab1_frame, text="Hasil Praktikum")
        self.notebook.add(bab2_frame, text="Tugas Praktikum")
        self.notebook.add(bab3_frame, text="Kesimpulan")
        self.notebook.add(generate_frame, text="Selesai")

        self.cover_tab = CoverTab(self, cover_frame)
        self.bab1_tab = Bab1Tab(self, bab1_frame)
        self.bab2_tab = Bab2Tab(self, bab2_frame)
        self.bab3_tab = Bab3Tab(self, bab3_frame)
        self.generate_tab = GenerateTab(self, generate_frame)