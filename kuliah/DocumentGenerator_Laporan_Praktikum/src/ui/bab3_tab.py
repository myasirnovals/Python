from tkinter import ttk
from tkinter import scrolledtext


class Bab3Tab(ttk.Frame):
    def __init__(self, app, parent):
        super().__init__(parent, padding=12)
        self.app = app
        self.kesimpulan_text = None
        self._build()

    def _build(self):
        self.pack(fill="both", expand=True)
        ttk.Label(self, text="Kesimpulan").pack(anchor="w")
        self.kesimpulan_text = scrolledtext.ScrolledText(
            self, wrap="word", height=16
        )
        self.kesimpulan_text.pack(fill="both", expand=True, pady=8)

    def get_kesimpulan(self):
        if not self.kesimpulan_text:
            return ""
        return self.kesimpulan_text.get("1.0", "end-1c")
