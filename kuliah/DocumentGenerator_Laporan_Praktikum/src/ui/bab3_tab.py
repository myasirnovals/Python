from tkinter import ttk
from tkinter import scrolledtext


def build_bab3_tab(app, parent):
    frame = ttk.Frame(parent, padding=12)
    frame.pack(fill="both", expand=True)

    ttk.Label(frame, text="Kesimpulan").pack(anchor="w")
    app.kesimpulan_text = scrolledtext.ScrolledText(frame, wrap="word", height=16)
    app.kesimpulan_text.pack(fill="both", expand=True, pady=8)
