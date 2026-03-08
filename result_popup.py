import tkinter as tk
from tkinter import messagebox


class ResultPopup:
    def __init__(self, parent, on_recapture, on_close):
        self._on_recapture = on_recapture
        self._on_close = on_close

        self.window = tk.Toplevel(parent)
        self.window.title("Iconiq Text Copy \u2014 Result")
        self.window.geometry("540x420")
        self.window.configure(bg="#1e1e2e")
        self.window.attributes("-topmost", True)
        self.window.resizable(True, True)
        self.window.minsize(320, 220)
        self.window.protocol("WM_DELETE_WINDOW", self._close)

        self._build_ui()
        self._center()
        self.window.focus_force()

    def _build_ui(self):
        header = tk.Label(
            self.window, text="Extracted Text",
            font=("Segoe UI", 13, "bold"),
            fg="#cdd6f4", bg="#1e1e2e",
        )
        header.pack(pady=(14, 6))

        text_frame = tk.Frame(self.window, bg="#313244")
        text_frame.pack(fill="both", expand=True, padx=14, pady=(0, 10))

        scrollbar = tk.Scrollbar(text_frame)
        scrollbar.pack(side="right", fill="y")

        self._text = tk.Text(
            text_frame, wrap="word",
            font=("Consolas", 11),
            bg="#313244", fg="#cdd6f4",
            insertbackground="#cdd6f4",
            selectbackground="#585b70",
            relief="flat", borderwidth=0,
            padx=12, pady=10,
            yscrollcommand=scrollbar.set,
        )
        self._text.pack(fill="both", expand=True)
        scrollbar.config(command=self._text.yview)

        self._text.insert("1.0", "Processing\u2026")
        self._text.config(fg="#a6adc8")

        btn_frame = tk.Frame(self.window, bg="#1e1e2e")
        btn_frame.pack(fill="x", padx=14, pady=(0, 14))

        self._copy_btn = tk.Button(
            btn_frame, text="\U0001F4CB  Copy",
            font=("Segoe UI", 10),
            fg="#1e1e2e", bg="#a6e3a1",
            activebackground="#94e2d5", activeforeground="#1e1e2e",
            relief="flat", cursor="hand2",
            padx=16, pady=6,
            command=self._copy,
        )
        self._copy_btn.pack(side="left", padx=(0, 8))

        recapture_btn = tk.Button(
            btn_frame, text="\U0001F504  Recapture",
            font=("Segoe UI", 10),
            fg="#1e1e2e", bg="#89b4fa",
            activebackground="#74c7ec", activeforeground="#1e1e2e",
            relief="flat", cursor="hand2",
            padx=16, pady=6,
            command=self._recapture,
        )
        recapture_btn.pack(side="left", padx=(0, 8))

        close_btn = tk.Button(
            btn_frame, text="\u2715  Close",
            font=("Segoe UI", 10),
            fg="#cdd6f4", bg="#45475a",
            activebackground="#585b70", activeforeground="#cdd6f4",
            relief="flat", cursor="hand2",
            padx=16, pady=6,
            command=self._close,
        )
        close_btn.pack(side="right")

    def _center(self):
        self.window.update_idletasks()
        w = self.window.winfo_width()
        h = self.window.winfo_height()
        x = (self.window.winfo_screenwidth() - w) // 2
        y = (self.window.winfo_screenheight() - h) // 2
        self.window.geometry(f"{w}x{h}+{x}+{y}")

    def set_text(self, text: str):
        self._text.config(state="normal")
        self._text.delete("1.0", "end")

        if not text:
            self._text.insert("1.0", "No text detected in the selected area.")
            self._text.config(fg="#a6adc8")
        elif text.startswith("[ERROR]"):
            self._text.insert("1.0", text)
            self._text.config(fg="#f38ba8")
        else:
            self._text.insert("1.0", text)
            self._text.config(fg="#cdd6f4")

    def _copy(self):
        content = self._text.get("1.0", "end-1c")
        if not content or content == "Processing\u2026":
            return
        try:
            self.window.clipboard_clear()
            self.window.clipboard_append(content)
            self.window.update()
            self._copy_btn.config(text="\u2713  Copied!", bg="#94e2d5")
            self.window.after(
                1500,
                lambda: self._copy_btn.config(text="\U0001F4CB  Copy", bg="#a6e3a1"),
            )
        except Exception:
            messagebox.showerror(
                "Clipboard Error",
                "Failed to copy text to clipboard.",
                parent=self.window,
            )

    def _recapture(self):
        self.window.destroy()
        self._on_recapture()

    def _close(self):
        self.window.destroy()
        self._on_close()
