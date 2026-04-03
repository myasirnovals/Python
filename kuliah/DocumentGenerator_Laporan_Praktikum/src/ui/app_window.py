import os
import sys
import tkinter as tk
from tkinter import ttk
from tkinterdnd2 import TkinterDnD
from PIL import Image, ImageTk

from app.ai_client import GeminiClient
from app.services.analysis_service import AnalysisService
from app.services.report_service import ReportService
from ui.cover_tab import CoverTab
from ui.results_tab import ResultsTab
from ui.tasks_tab import TasksTab
from ui.conclusion_tab import ConclusionTab
from ui.generate_tab import GenerateTab
from ui.styles import setup_styles

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
TEMPLATES_DIR = os.path.join(BASE_DIR, "..", "templates")
ASSETS_DIR = os.path.join(BASE_DIR, "..", "assets")


class App(TkinterDnD.Tk):
    def __init__(self):
        super().__init__()
        self.title("Lab Report Generator Pro")

        # --- UPDATE UKURAN (FINAL) ---
        # Lebar: 950
        # Tinggi: 630 (Naik dikit dari 600 biar ada napas di bawah)
        screen_w = self.winfo_screenwidth()
        screen_h = self.winfo_screenheight()

        is_compact = screen_w < 1400 or screen_h < 850
        target_width = 910 if is_compact else 980
        target_height = 610 if is_compact else 670

        x_pos = (screen_w - target_width) // 2
        y_pos = (screen_h - target_height) // 2

        self.geometry(f"{target_width}x{target_height}+{x_pos}+{y_pos}")
        self.minsize(780, 530)
        self.is_compact_mode = is_compact
        # -----------------------------

        setup_styles(self)

        self.ai_client = GeminiClient()
        self.analysis_service = AnalysisService(self.ai_client)
        self.report_service = ReportService(TEMPLATES_DIR)

        self.cover_tab = None
        self.results_tab = None
        self.tasks_tab = None
        self.conclusion_tab = None
        self.generate_tab = None
        self.logo_image = None

        self._build_ui()

    def _get_logo_path(self):
        bundled_base = getattr(sys, "_MEIPASS", None)
        if bundled_base:
            bundled_logo = os.path.join(bundled_base, "assets", "logo.jpeg")
            if os.path.exists(bundled_logo):
                return bundled_logo

        local_logo = os.path.join(ASSETS_DIR, "logo.jpeg")
        if os.path.exists(local_logo):
            return local_logo

        return None

    def _load_logo_image(self):
        logo_path = self._get_logo_path()
        if not logo_path:
            return None

        image = Image.open(logo_path)
        image = image.resize((48, 48), Image.Resampling.LANCZOS)
        return ImageTk.PhotoImage(image)

    def _build_ui(self):
        self.configure(bg="#f3f6fb")

        outer_pad = 10 if getattr(self, "is_compact_mode", False) else 15
        main_container = ttk.Frame(self)
        main_container.pack(fill="both", expand=True, padx=outer_pad, pady=outer_pad)

        content_canvas = tk.Canvas(main_container, highlightthickness=0, bg="#f3f6fb")
        content_scrollbar = ttk.Scrollbar(
            main_container, orient="vertical", command=content_canvas.yview
        )
        content_canvas.configure(yscrollcommand=content_scrollbar.set)

        content_scrollbar.pack(side="right", fill="y")
        content_canvas.pack(side="left", fill="both", expand=True)

        scrollable_content = ttk.Frame(content_canvas)
        canvas_window = content_canvas.create_window(
            (0, 0), window=scrollable_content, anchor="nw"
        )

        def _on_content_configure(event):
            content_canvas.configure(scrollregion=content_canvas.bbox("all"))

        def _on_canvas_configure(event):
            content_canvas.itemconfigure(canvas_window, width=event.width)

        scrollable_content.bind("<Configure>", _on_content_configure)
        content_canvas.bind("<Configure>", _on_canvas_configure)

        def _on_mousewheel(event):
            content_canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")

        content_canvas.bind_all("<MouseWheel>", _on_mousewheel)

        header_frame = ttk.Frame(scrollable_content)
        header_frame.pack(fill="x", pady=(0, 8 if self.is_compact_mode else 10))

        self.logo_image = self._load_logo_image()
        if self.logo_image:
            ttk.Label(header_frame, image=self.logo_image).pack(side="left", padx=(0, 10))

        ttk.Label(header_frame, text="Lab Report Generator", style="Header.TLabel").pack(
            side="left"
        )
        ttk.Label(header_frame, text="v4.2.7", style="Muted.TLabel").pack(
            side="left", padx=(10, 0), pady=(4, 0)
        )
        ttk.Label(
            header_frame,
            text="AI Assisted",
            background="#dbeafe",
            foreground="#1d4ed8",
            font=("Segoe UI", 9, "bold"),
            padding=(8, 3),
        ).pack(side="left", padx=8, pady=(2, 0))

        notebook_container = ttk.Frame(
            scrollable_content,
            padding=(8 if self.is_compact_mode else 10),
        )
        notebook_container.pack(fill="both", expand=True)

        self.notebook = ttk.Notebook(notebook_container)
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
        self.results_tab = ResultsTab(self, bab1_frame)
        self.tasks_tab = TasksTab(self, bab2_frame)
        self.conclusion_tab = ConclusionTab(self, bab3_frame)
        self.generate_tab = GenerateTab(self, generate_frame)

