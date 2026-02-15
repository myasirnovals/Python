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

        bg_main = "#f8f9fa"
        accent_blue = "#007bff"
        text_dark = "#212529"

        style.configure("TFrame", background=bg_main)
        style.configure(
                "TLabel", background=bg_main, foreground=text_dark, font=("Segoe UI", base_font)
        )
        style.configure(
                "Header.TLabel", font=("Segoe UI", header_font, "bold"), foreground=accent_blue
        )
        style.configure("Subheader.TLabel", font=("Segoe UI", base_font + 1, "bold"))

        style.configure("TNotebook", background=bg_main, borderwidth=0)
        style.configure("TNotebook.Tab", padding=tab_padding, font=("Segoe UI", base_font))
        style.map(
                "TNotebook.Tab",
                background=[("selected", accent_blue)],
                foreground=[("selected", "white")],
        )

        style.configure("TButton", font=("Segoe UI", base_font), padding=6)
        style.configure(
                "Action.TButton",
                font=("Segoe UI", base_font, "bold"),
                foreground="white",
                background=accent_blue,
        )
        style.map("Action.TButton", background=[("active", "#0056b3")])

        style.configure("TLabelframe", background=bg_main, relief="groove")
        style.configure(
                "TLabelframe.Label", background=bg_main, font=("Segoe UI", base_font, "bold")
        )