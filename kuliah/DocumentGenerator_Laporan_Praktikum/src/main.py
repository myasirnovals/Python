import os
import sys
from ui.app_window import App

# --- Tambahkan fungsi ini di sini ---
def resource_path(relative_path):
    """ Dapatkan path absolut ke resource, berfungsi untuk dev dan PyInstaller """
    try:
        # PyInstaller membuat folder temp dan menyimpan path di _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)

def main():
    app = App()
    app.mainloop()

if __name__ == "__main__":
    main()