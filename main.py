import sys
import ctypes


def configure_dpi():
    if sys.platform == "win32":
        try:
            ctypes.windll.shcore.SetProcessDpiAwareness(2)
        except Exception:
            try:
                ctypes.windll.user32.SetProcessDPIAware()
            except Exception:
                pass


if __name__ == "__main__":
    configure_dpi()
    from app import IconiqShot
    app = IconiqShot()
    app.run()
