from tkinter import ttk


def setup_styles(root):
        """Konfigurasi tema dan gaya visual aplikasi."""
        style = ttk.Style(root)
        style.theme_use("clam")

        # Sesuaikan ukuran font berdasarkan lebar layar agar tampak konsisten
        sw = root.winfo_screenwidth()
        if sw < 1280:
            base_font = 9
            header_font = 13
            tab_padding = [12, 8]
        elif sw < 1920:
            base_font = 10
            header_font = 14
            tab_padding = [18, 10]
        else:
            base_font = 11
            header_font = 16
            tab_padding = [22, 12]

        bg_main = "#f3f6fb"
        panel_bg = "#ffffff"
        accent_blue = "#2563eb"
        accent_blue_hover = "#1d4ed8"
        accent_soft = "#dbeafe"
        text_dark = "#0f172a"
        text_muted = "#475569"

        style.configure("TFrame", background=bg_main)
        style.configure(
                "TLabel", background=bg_main, foreground=text_dark, font=("Segoe UI", base_font)
        )
        style.configure(
                "Header.TLabel", font=("Segoe UI", header_font, "bold"), foreground=accent_blue
        )
        style.configure("Subheader.TLabel", font=("Segoe UI", base_font + 1, "bold"), foreground=text_muted)
        style.configure("Muted.TLabel", background=bg_main, foreground=text_muted, font=("Segoe UI", base_font))

        style.configure("TNotebook", background=bg_main, borderwidth=0)
        style.configure(
                "TNotebook.Tab",
                padding=[tab_padding[0], tab_padding[1] + 1],
                font=("Segoe UI", base_font, "bold"),
                background="#e2e8f0",
                foreground="#334155",
                borderwidth=0,
        )
        style.map(
                "TNotebook.Tab",
                background=[("selected", accent_blue), ("active", accent_soft)],
                foreground=[("selected", "white"), ("active", accent_blue_hover)],
        )

        style.configure(
                "TButton",
                font=("Segoe UI", base_font),
                padding=[10, 7],
                background=panel_bg,
                foreground=text_dark,
                borderwidth=0,
        )
        style.map(
                "TButton",
                background=[("active", "#e2e8f0")],
        )
        style.configure(
                "Action.TButton",
                font=("Segoe UI", base_font, "bold"),
                foreground="white",
                background=accent_blue,
                borderwidth=0,
                padding=[12, 8],
        )
        style.map("Action.TButton", background=[("active", accent_blue_hover)])

        style.configure("Card.TLabelframe", background=panel_bg, relief="flat", borderwidth=1)
        style.configure("Card.TLabelframe.Label", background=panel_bg, foreground=text_dark, font=("Segoe UI", base_font, "bold"))
        style.configure("TLabelframe", background=panel_bg, relief="flat", borderwidth=1)
        style.configure(
                "TLabelframe.Label", background=panel_bg, foreground=text_dark, font=("Segoe UI", base_font, "bold")
        )

        style.configure(
                "Treeview",
                font=("Segoe UI", base_font),
                rowheight=28,
                background=panel_bg,
                foreground=text_dark,
                fieldbackground=panel_bg,
                borderwidth=0,
        )
        style.configure(
                "Treeview.Heading",
                font=("Segoe UI", base_font, "bold"),
                background="#e2e8f0",
                foreground="#334155",
                relief="flat",
                padding=(8, 6),
        )
        style.map(
                "Treeview",
                background=[("selected", accent_soft)],
                foreground=[("selected", accent_blue_hover)],
        )