import os
import sys
import traceback


def _harden_stdio():
    """Pastikan print() tidak pernah membuat aplikasi crash.

    - .exe tanpa console (PyInstaller console=False): sys.stdout / sys.stderr = None.
    - Console Windows (cp1252): print emoji melempar UnicodeEncodeError.
    """
    for name in ("stdout", "stderr"):
        stream = getattr(sys, name, None)
        if stream is None:
            setattr(sys, name, open(os.devnull, "w", encoding="utf-8"))
        elif hasattr(stream, "reconfigure"):
            try:
                stream.reconfigure(encoding="utf-8", errors="replace")
            except Exception:
                pass


def _crash_log_path():
    base = os.path.dirname(sys.executable) if getattr(sys, "frozen", False) else os.path.abspath(".")
    return os.path.join(base, "crash.log")


def _log_exception(exc_type, exc, tb):
    """Tulis traceback ke crash.log supaya error di .exe bisa dilacak."""
    try:
        with open(_crash_log_path(), "a", encoding="utf-8") as f:
            f.write("".join(traceback.format_exception(exc_type, exc, tb)))
            f.write("\n")
    except Exception:
        pass


def _report_callback_exception(exc_type, exc, tb):
    """Error di callback Tk (klik tombol dll.): catat ke log dan beri tahu user."""
    _log_exception(exc_type, exc, tb)
    try:
        from tkinter import messagebox

        messagebox.showerror(
            "Kesalahan",
            f"{exc_type.__name__}: {exc}\n\nDetail tersimpan di:\n{_crash_log_path()}",
        )
    except Exception:
        pass


_harden_stdio()
sys.excepthook = _log_exception

from ui.core.app_window import App  # noqa: E402

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
        app.report_callback_exception = _report_callback_exception
        app.mainloop()

def main():
    AppBootstrap.run()

if __name__ == "__main__":
    main()