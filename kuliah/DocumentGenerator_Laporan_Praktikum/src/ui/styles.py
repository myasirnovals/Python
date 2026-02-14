from tkinter import ttk


def setup_styles(root):
        """Konfigurasi tema dan gaya visual aplikasi."""
        style = ttk.Style(root)
        style.theme_use("clam")

        bg_main = "#f8f9fa"
        accent_blue = "#007bff"
        text_dark = "#212529"

        style.configure("TFrame", background=bg_main)
        style.configure(
                "TLabel", background=bg_main, foreground=text_dark, font=("Segoe UI", 10)
        )
        style.configure(
                "Header.TLabel", font=("Segoe UI", 14, "bold"), foreground=accent_blue
        )
        style.configure("Subheader.TLabel", font=("Segoe UI", 11, "bold"))

        style.configure("TNotebook", background=bg_main, borderwidth=0)
        style.configure("TNotebook.Tab", padding=[20, 10], font=("Segoe UI", 10))
        style.map(
                "TNotebook.Tab",
                background=[("selected", accent_blue)],
                foreground=[("selected", "white")],
        )

        style.configure("TButton", font=("Segoe UI", 10), padding=6)
        style.configure(
                "Action.TButton",
                font=("Segoe UI", 10, "bold"),
                foreground="white",
                background=accent_blue,
        )
        style.map("Action.TButton", background=[("active", "#0056b3")])

        style.configure("TLabelframe", background=bg_main, relief="groove")
        style.configure(
                "TLabelframe.Label", background=bg_main, font=("Segoe UI", 10, "bold")
        )