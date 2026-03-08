import os
import sys

import pytesseract
from PIL import Image


class OCREngine:
    def __init__(self):
        self._configure()

    def _configure(self):
        if sys.platform != "win32":
            return

        env_path = os.environ.get("TESSERACT_CMD", "")
        if env_path and os.path.isfile(env_path):
            pytesseract.pytesseract.tesseract_cmd = env_path
            return

        candidates = [
            r"C:\Program Files\Tesseract-OCR\tesseract.exe",
            r"C:\Program Files (x86)\Tesseract-OCR\tesseract.exe",
            os.path.join(
                os.environ.get("LOCALAPPDATA", ""), "Tesseract-OCR", "tesseract.exe"
            ),
        ]
        for path in candidates:
            if os.path.isfile(path):
                pytesseract.pytesseract.tesseract_cmd = path
                return

    def extract_text(self, image: Image.Image) -> str:
        if image is None:
            return "[ERROR] No image provided for OCR."
        try:
            rgb = image.convert("RGB")
            text: str = pytesseract.image_to_string(rgb, lang="eng")
            return text.strip()
        except pytesseract.TesseractNotFoundError:
            return (
                "[ERROR] Tesseract OCR engine not found.\n\n"
                "Install it from:\n"
                "https://github.com/UB-Mannheim/tesseract/wiki\n\n"
                "After installing, restart this application."
            )
        except Exception as exc:
            return f"[ERROR] OCR failed: {exc}"
