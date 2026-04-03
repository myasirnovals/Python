"""base.py - Base class for all UI tabs with common patterns."""

from tkinter import ttk
from ui.utils import show_info, show_warning, show_error


class BaseTab(ttk.Frame):
    """
    Base class for all UI tabs.
    
    Provides common functionality, styling, and helpers for subclasses.
    Subclasses should override _build() to implement specific UI.
    """
    
    def __init__(self, app, parent):
        """
        Initialize base tab.
        
        Args:
            app: Main App instance with services
            parent: Parent widget (usually a ttk.Frame from notebook)
        """
        super().__init__(parent, padding=20)
        self.app = app
        self._build()
    
    def _build(self):
        """Build tab UI. Override in subclasses."""
        raise NotImplementedError("Subclasses must implement _build()")
    
    def pack_fill_expand(self) -> None:
        """Pack tab to fill parent with expand."""
        self.pack(fill="both", expand=True)
    
    def _add_header(self, title: str, style: str = "Header.TLabel") -> ttk.Frame:
        """
        Add a header section to the tab.
        
        Args:
            title: Header text
            style: ttk style for the label
        
        Returns:
            Frame containing the header
        """
        header_frame = ttk.Frame(self)
        header_frame.pack(fill="x", pady=(0, 10))
        ttk.Label(header_frame, text=title, style=style).pack(side="left")
        return header_frame
    
    def _add_button_group(self, parent, buttons: list, pady=10) -> ttk.Frame:
        """
        Add a group of buttons in a frame.
        
        Args:
            parent: Parent widget
            buttons: List of tuples (text, command)
            pady: Padding
        
        Returns:
            Frame containing the buttons
        """
        btn_frame = ttk.Frame(parent)
        btn_frame.pack(fill="x", pady=pady)
        
        for text, command in buttons:
            ttk.Button(btn_frame, text=text, command=command).pack(side="left", padx=2)
        
        return btn_frame
    
    def _add_labeled_entry(self, parent, label_text: str, textvariable) -> ttk.Frame:
        """
        Add a label + entry field pair.
        
        Returns:
            Frame containing both widgets
        """
        frame = ttk.Frame(parent)
        frame.pack(fill="x", pady=5)
        ttk.Label(frame, text=label_text).pack(anchor="w")
        ttk.Entry(frame, textvariable=textvariable).pack(fill="x")
        return frame
    
    def _add_section(self, parent, title: str, padding: int = 10) -> ttk.LabelFrame:
        """
        Add a labeled section frame.
        
        Args:
            parent: Parent widget
            title: Section title
            padding: Internal padding
        
        Returns:
            LabelFrame for content
        """
        section = ttk.LabelFrame(parent, text=f" {title} ", padding=padding)
        section.pack(fill="x", pady=(0, 10))
        return section
    
    def show_info(self, title: str, message: str) -> None:
        """Show info dialog."""
        show_info(title, message, parent=self)
    
    def show_warning(self, title: str, message: str) -> None:
        """Show warning dialog."""
        show_warning(title, message, parent=self)
    
    def show_error(self, title: str, message: str) -> None:
        """Show error dialog."""
        show_error(title, message, parent=self)
