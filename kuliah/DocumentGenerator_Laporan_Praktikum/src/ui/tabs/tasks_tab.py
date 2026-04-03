"""Tasks tab (OOP tab layer)."""

from ui.components.code_image.code_image_tab import CodeImageTab
from ui.constants import TAB_LABEL_TASKS


class TasksTab(CodeImageTab):
    def __init__(self, app, parent):
        super().__init__(app, parent, section_name=TAB_LABEL_TASKS, max_items=None)

    def _supports_qa_content(self):
        return True
