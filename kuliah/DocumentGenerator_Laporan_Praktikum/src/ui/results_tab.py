"""results_tab.py - Lab results section with code and image management."""

from ui.code_image_tab import CodeImageTab
from ui.constants import TAB_LABEL_RESULTS


class ResultsTab(CodeImageTab):
    """
    Tab for managing lab results (Hasil Praktikum).
    
    Inherits from CodeImageTab to support code files, images, and AI generation.
    """
    
    def __init__(self, app, parent):
        super().__init__(app, parent, section_name=TAB_LABEL_RESULTS, max_items=None)
