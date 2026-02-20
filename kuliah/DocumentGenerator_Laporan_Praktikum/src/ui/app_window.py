import os
import sys
import tkinter as tk
from tkinter import messagebox, simpledialog, ttk
from PIL import Image, ImageTk

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
ASSETS_DIR = os.path.join(BASE_DIR, "..", "assets")


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
        self.configure(bg="#f8f9fa")

        # Padding 15 tetap, nanti akan terlihat pas dengan tinggi 630
        main_container = ttk.Frame(self)
        main_container.pack(fill="both", expand=True, padx=15, pady=15)

        content_canvas = tk.Canvas(main_container, highlightthickness=0, bg="#f8f9fa")
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
        header_frame.pack(fill="x", pady=(0, 10))

        self.logo_image = self._load_logo_image()
        if self.logo_image:
            ttk.Label(header_frame, image=self.logo_image).pack(side="left", padx=(0, 10))

        ttk.Label(header_frame, text="Lab Report Generator", style="Header.TLabel").pack(
            side="left"
        )
        ttk.Label(
            header_frame, text="v3.10.1 Beta", foreground="#6c757d"
        ).pack(side="left", padx=10, pady=(5, 0))

        ttk.Button(
            header_frame,
            text="Input AI_API_KEY",
            command=self._prompt_api_key,
        ).pack(side="right")

        self.notebook = ttk.Notebook(scrollable_content)
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

    def _prompt_api_key(self):
        api_key = simpledialog.askstring(
            "AI API Key",
            "Masukkan AI_API_KEY (Gemini API Key):",
            parent=self,
            show="*",
        )

        if api_key is None:
            return

        cleaned_key = api_key.strip()
        if not cleaned_key:
            messagebox.showwarning("Input Kosong", "AI_API_KEY tidak boleh kosong.")
            return

        os.environ["AI_API_KEY"] = cleaned_key
        os.environ["GEMINI_API_KEY"] = cleaned_key
        self.ai_client.api_key = cleaned_key
        self.ai_client.model_name = None

        messagebox.showinfo("Berhasil", "AI_API_KEY berhasil diperbarui untuk sesi ini.")