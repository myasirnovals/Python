"""Base class for UI tabs (OOP core)."""

from tkinter import ttk
from ui.utils import UIUtils


class BaseTab(ttk.Frame):
    """Base class for all tab views."""

    def __init__(self, app, parent):
        super().__init__(parent, padding=20)
        self.app = app
        self._build()

    def _build(self):
        raise NotImplementedError("Subclasses must implement _build()")

    def pack_fill_expand(self) -> None:
        self.pack(fill="both", expand=True)

    def _add_header(self, title: str, style: str = "Header.TLabel") -> ttk.Frame:
        header_frame = ttk.Frame(self)
        header_frame.pack(fill="x", pady=(0, 10))
        ttk.Label(header_frame, text=title, style=style).pack(side="left")
        return header_frame

    def _add_button_group(self, parent, buttons: list, pady=10) -> ttk.Frame:
        btn_frame = ttk.Frame(parent)
        btn_frame.pack(fill="x", pady=pady)
        for text, command in buttons:
            ttk.Button(btn_frame, text=text, command=command).pack(side="left", padx=2)
        return btn_frame

    def show_info(self, title: str, message: str) -> None:
        UIUtils.show_info(title, message, parent=self)

    def show_warning(self, title: str, message: str) -> None:
        UIUtils.show_warning(title, message, parent=self)

    def show_error(self, title: str, message: str) -> None:
        UIUtils.show_error(title, message, parent=self)
