import os
import sys
from ui.core.app_window import App

class AppBootstrap:
    """Application entrypoint orchestration."""

    @staticmethod
    def resource_path(relative_path):
        """Dapatkan path absolut ke resource, berfungsi untuk dev dan PyInstaller."""
        try:
            base_path = sys._MEIPASS
        except Exception:
            base_path = os.path.abspath(".")

        return os.path.join(base_path, relative_path)

    @staticmethod
    def run():
        app = App()
        app.mainloop()

def main():
    AppBootstrap.run()

if __name__ == "__main__":
    main()