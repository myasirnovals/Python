"""tasks_tab.py - Lab tasks section with code and image management."""

from ui.code_image_tab import CodeImageTab
from ui.constants import TAB_LABEL_TASKS


class TasksTab(CodeImageTab):
    """
    Tab for managing lab tasks (Tugas Praktikum).
    
    Inherits from CodeImageTab to support code files, images, and AI generation.
    Functionally identical to ResultsTab but with different section label.
    """
    
    def __init__(self, app, parent):
        super().__init__(app, parent, section_name=TAB_LABEL_TASKS, max_items=None)
