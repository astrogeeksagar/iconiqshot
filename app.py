import tkinter as tk
from tkinter import messagebox
import threading
import os
from datetime import datetime

from overlay import CaptureOverlay
from ocr_engine import OCREngine


class IconiqShot:
    """Iconiq Shot — Lightshot-style screen text capture utility."""

    # ── Theme ──
    _BG = "#1c1c2b"
    _SURFACE = "#252538"
    _BORDER = "#2f2f45"
    _TEXT = "#d4d6e4"
    _SUBTEXT = "#8a8da0"
    _MUTED = "#5c5f72"
    _ACCENT = "#4ea8f0"
    _GREEN = "#6fcf8a"
    _TEAL = "#5ac8b8"
    _YELLOW = "#e8c76a"
    _RED = "#e06070"
    _BAR_BG = "#16162a"
    _BTN_BG = "#2a2a40"
    _BTN_HOVER = "#363650"

    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Iconiq Shot")
        self.root.geometry("580x480")
        self.root.minsize(480, 400)
        self.root.configure(bg=self._BG)
        self.root.protocol("WM_DELETE_WINDOW", self._quit)

        self.ocr = OCREngine()
        self._captured_image = None
        self._result_visible = False

        self._build_ui()
        self._center_window()

    # ── Landing UI ──

    def _build_ui(self):
        # Status bar (always at bottom)
        status_bar = tk.Frame(self.root, bg=self._BAR_BG, height=28)
        status_bar.pack(side="bottom", fill="x")
        status_bar.pack_propagate(False)
        self._status = tk.Label(
            status_bar, text="Ready", font=("Segoe UI", 8),
            fg=self._SUBTEXT, bg=self._BAR_BG, anchor="w",
        )
        self._status.pack(fill="x", padx=16, pady=5)

        # Landing view — centered content
        self._landing = tk.Frame(self.root, bg=self._BG)
        self._landing.pack(fill="both", expand=True)

        spacer = tk.Frame(self._landing, bg=self._BG)
        spacer.pack(expand=True)

        tk.Label(
            self._landing, text="Iconiq Shot",
            font=("Segoe UI", 26, "bold"),
            fg=self._TEXT, bg=self._BG,
        ).pack()

        tk.Label(
            self._landing, text="Screen Text Capture",
            font=("Segoe UI", 10), fg=self._SUBTEXT, bg=self._BG,
        ).pack(pady=(2, 28))

        cap_btn = tk.Button(
            self._landing, text="New Capture",
            font=("Segoe UI", 12, "bold"),
            fg="#ffffff", bg=self._ACCENT,
            activebackground="#3d94d8", activeforeground="#ffffff",
            relief="flat", cursor="hand2",
            padx=30, pady=10,
            command=self.start_capture,
        )
        cap_btn.pack()

        tk.Label(
            self._landing, text="or press Ctrl+N",
            font=("Segoe UI", 9), fg=self._MUTED, bg=self._BG,
        ).pack(pady=(8, 0))

        spacer2 = tk.Frame(self._landing, bg=self._BG)
        spacer2.pack(expand=True)

        # Result view (hidden initially)
        self._result_frame = tk.Frame(self.root, bg=self._BG)

        self._build_result_view()

        # Keyboard shortcut
        self.root.bind("<Control-n>", lambda e: self.start_capture())
        self.root.bind("<Control-N>", lambda e: self.start_capture())

    def _build_result_view(self):
        # Header row
        hdr = tk.Frame(self._result_frame, bg=self._BG)
        hdr.pack(fill="x", padx=20, pady=(16, 0))

        tk.Label(
            hdr, text="Extracted Text",
            font=("Segoe UI", 14, "bold"),
            fg=self._TEXT, bg=self._BG,
        ).pack(side="left")

        # Action buttons row (right-aligned in header)
        self._copy_btn = self._make_action_btn(
            hdr, "Copy", self._GREEN, self._copy_text,
        )
        self._copy_btn.pack(side="right", padx=(6, 0))

        self._save_btn = self._make_action_btn(
            hdr, "Save Image", self._YELLOW, self._save_image,
        )
        self._save_btn.pack(side="right", padx=(6, 0))

        recap_btn = self._make_action_btn(
            hdr, "New Capture", self._ACCENT, self.start_capture,
        )
        recap_btn.pack(side="right", padx=(6, 0))

        clear_btn = self._make_action_btn(
            hdr, "Clear", self._MUTED, self._clear,
        )
        clear_btn.pack(side="right", padx=(6, 0))

        # Separator
        tk.Frame(self._result_frame, bg=self._BORDER, height=1).pack(
            fill="x", padx=20, pady=(12, 0),
        )

        # Scrollable text area
        text_frame = tk.Frame(self._result_frame, bg=self._SURFACE)
        text_frame.pack(fill="both", expand=True, padx=20, pady=(10, 16))

        scrollbar = tk.Scrollbar(text_frame)
        scrollbar.pack(side="right", fill="y")

        self._text = tk.Text(
            text_frame, wrap="word",
            font=("Consolas", 11),
            bg=self._SURFACE, fg=self._TEXT,
            insertbackground=self._TEXT,
            selectbackground="#404060",
            relief="flat", borderwidth=0,
            padx=14, pady=12,
            yscrollcommand=scrollbar.set,
        )
        self._text.pack(fill="both", expand=True)
        scrollbar.config(command=self._text.yview)

    def _make_action_btn(self, parent, text, color, command):
        btn = tk.Button(
            parent, text=text,
            font=("Segoe UI", 9),
            fg=self._BG, bg=color,
            activeforeground=self._BG,
            activebackground=color,
            relief="flat", cursor="hand2",
            padx=10, pady=3,
            command=command,
        )
        return btn

    # ── View switching ──

    def _show_result_view(self):
        if not self._result_visible:
            self._landing.pack_forget()
            self._result_frame.pack(fill="both", expand=True)
            self._result_visible = True
            # Expand window for result content
            self.root.geometry("680x520")
            self.root.minsize(550, 420)

    def _show_landing(self):
        if self._result_visible:
            self._result_frame.pack_forget()
            self._landing.pack(fill="both", expand=True)
            self._result_visible = False
            self.root.geometry("580x480")
            self.root.minsize(480, 400)

    # ── Helpers ──

    def _center_window(self):
        self.root.update_idletasks()
        w = self.root.winfo_width()
        h = self.root.winfo_height()
        sw = self.root.winfo_screenwidth()
        sh = self.root.winfo_screenheight()
        self.root.geometry(f"{w}x{h}+{(sw - w) // 2}+{(sh - h) // 2}")

    def _set_status(self, msg):
        self._status.config(text=msg)

    def _set_text(self, content, color):
        self._text.delete("1.0", "end")
        self._text.insert("1.0", content)
        self._text.config(fg=color)

    # ── Capture flow ──

    def start_capture(self):
        self._set_status("Select a screen region...")
        self.root.withdraw()
        self.root.after(250, self._launch_overlay)

    def _launch_overlay(self):
        CaptureOverlay(self.root, self._on_capture, self._on_cancel)

    def _on_capture(self, image, action="extract"):
        self._captured_image = image
        self.root.deiconify()

        if action == "save":
            self._save_image()
            self._show_result_view()
            self._set_text("Image saved. Use Extract Text or Copy Text from a new capture.", self._SUBTEXT)
            self._set_status("Image saved")
            return

        if action == "copy":
            self._show_result_view()
            self._set_text("Extracting text...", self._SUBTEXT)
            self._set_status("Running OCR...")
            thread = threading.Thread(
                target=self._run_ocr, args=(image, True), daemon=True,
            )
            thread.start()
            return

        # Default: extract and display
        self._show_result_view()
        self._set_text("Extracting text...", self._SUBTEXT)
        self._set_status("Running OCR...")
        thread = threading.Thread(
            target=self._run_ocr, args=(image, False), daemon=True,
        )
        thread.start()

    def _run_ocr(self, image, auto_copy):
        text = self.ocr.extract_text(image)
        self.root.after(0, self._show_result, text, auto_copy)

    def _show_result(self, text, auto_copy=False):
        if not text:
            self._set_text("No text detected in the selected area.", self._SUBTEXT)
            self._set_status("No text detected")
        elif text.startswith("[ERROR]"):
            self._set_text(text, self._RED)
            self._set_status("OCR error")
        else:
            self._set_text(text, self._TEXT)
            self._set_status("Text extracted")
            if auto_copy:
                self.root.after(100, self._copy_text)

    def _on_cancel(self, recapture=False):
        self.root.deiconify()
        if recapture:
            self.root.after(200, self.start_capture)
        else:
            self._set_status("Cancelled")

    # ── Actions ──

    def _copy_text(self):
        content = self._text.get("1.0", "end-1c").strip()
        skip = {"", "Extracting text..."}
        if content in skip:
            self._set_status("Nothing to copy")
            return
        if content.startswith("[ERROR]"):
            self._set_status("Cannot copy error text")
            return
        try:
            self.root.clipboard_clear()
            self.root.clipboard_append(content)
            self.root.update()
            self._copy_btn.config(text="Copied!", bg=self._TEAL)
            self._set_status("Text copied to clipboard")
            self.root.after(
                1500,
                lambda: self._copy_btn.config(text="Copy", bg=self._GREEN),
            )
        except Exception:
            messagebox.showerror(
                "Clipboard Error",
                "Failed to copy text to clipboard.",
                parent=self.root,
            )
            self._set_status("Clipboard error")

    def _save_image(self):
        if self._captured_image is None:
            self._set_status("No image to save — capture a region first")
            return
        try:
            save_dir = os.path.join(
                os.path.expanduser("~"),
                "Pictures", "iconiqshots", "imagesall",
            )
            os.makedirs(save_dir, exist_ok=True)
            ts = datetime.now().strftime("%Y_%m_%d_%H_%M_%S")
            filepath = os.path.join(save_dir, f"capture_{ts}.png")
            self._captured_image.save(filepath, "PNG")
            self._save_btn.config(text="Saved!", bg=self._TEAL)
            self._set_status(f"Saved: {filepath}")
            self.root.after(
                2000,
                lambda: self._save_btn.config(text="Save Image", bg=self._YELLOW),
            )
        except Exception as exc:
            messagebox.showerror(
                "Save Error", f"Failed to save image:\n{exc}",
                parent=self.root,
            )
            self._set_status("Save failed")

    def _clear(self):
        self._captured_image = None
        self._show_landing()
        self._set_status("Ready")

    def _quit(self):
        self.root.destroy()

    def run(self):
        self.root.mainloop()
