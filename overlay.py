import tkinter as tk
from PIL import Image, ImageEnhance, ImageTk, ImageGrab, ImageDraw
from tooltip import ToolTip


class CaptureOverlay:
    """Full-screen overlay with drag selection and Lightshot-style floating toolbar."""

    # ── Visual constants ──
    _DIM = 0.35
    _SEL_BORDER = "#00a8ff"
    _SEL_WIDTH = 2
    _TB_BG = "#1e1e2e"
    _TB_BTN = "#2b2d3a"
    _TB_BTN_HOVER = "#3b3d4e"
    _TB_ICON_FG = "#c8cee0"
    _TB_ACCENT = "#00a8ff"
    _SIZE_BG = "#1a1a2a"
    _SIZE_FG = "#a0a8c0"

    def __init__(self, parent, on_capture, on_cancel):
        self._parent = parent
        self._on_capture = on_capture
        self._on_cancel = on_cancel
        self._start_x = 0
        self._start_y = 0
        self._dragging = False
        self._selection_done = False
        self._rect_id = None
        self._clear_id = None
        self._clear_photo = None
        self._size_id = None
        self._toolbar_frame = None
        self._sel_coords = None
        self._captured_image = None

        self._screenshot = ImageGrab.grab()
        self._dimmed = ImageEnhance.Brightness(self._screenshot).enhance(self._DIM)

        self.window = tk.Toplevel(parent)
        self.window.overrideredirect(True)
        self.window.attributes("-topmost", True)
        self.window.configure(cursor="crosshair")

        self._sw, self._sh = self._screenshot.size
        self.window.geometry(f"{self._sw}x{self._sh}+0+0")

        self._canvas = tk.Canvas(
            self.window, width=self._sw, height=self._sh,
            highlightthickness=0, cursor="crosshair",
        )
        self._canvas.pack(fill="both", expand=True)

        self._dimmed_photo = ImageTk.PhotoImage(self._dimmed)
        self._canvas.create_image(0, 0, anchor="nw", image=self._dimmed_photo)

        self._canvas.create_text(
            self._sw // 2, 38,
            text="Drag to select a region  \u00B7  Press Escape to cancel",
            font=("Segoe UI", 14), fill="#ffffff",
            tags="hint",
        )

        self._canvas.bind("<ButtonPress-1>", self._press)
        self._canvas.bind("<B1-Motion>", self._drag)
        self._canvas.bind("<ButtonRelease-1>", self._release)
        self.window.bind("<Escape>", self._cancel)

        self.window.grab_set()
        self.window.focus_force()

    # ── Coordinate helpers ──

    def _coords(self, event):
        x1 = max(0, min(self._start_x, event.x))
        y1 = max(0, min(self._start_y, event.y))
        x2 = min(self._sw, max(self._start_x, event.x))
        y2 = min(self._sh, max(self._start_y, event.y))
        return x1, y1, x2, y2

    # ── Mouse events ──

    def _press(self, event):
        if self._selection_done:
            return
        self._start_x = event.x
        self._start_y = event.y
        self._dragging = True
        self._canvas.delete("hint")

    def _drag(self, event):
        if not self._dragging or self._selection_done:
            return
        x1, y1, x2, y2 = self._coords(event)

        if self._rect_id:
            self._canvas.delete(self._rect_id)
        if self._clear_id:
            self._canvas.delete(self._clear_id)
        if self._size_id:
            self._canvas.delete(self._size_id)

        if x2 - x1 > 2 and y2 - y1 > 2:
            crop = self._screenshot.crop((x1, y1, x2, y2))
            self._clear_photo = ImageTk.PhotoImage(crop)
            self._clear_id = self._canvas.create_image(
                x1, y1, anchor="nw", image=self._clear_photo,
            )

        self._rect_id = self._canvas.create_rectangle(
            x1, y1, x2, y2,
            outline=self._SEL_BORDER, width=self._SEL_WIDTH,
        )

        w_sel = abs(x2 - x1)
        h_sel = abs(y2 - y1)
        if w_sel > 10 and h_sel > 10:
            size_text = f"{w_sel}\u00D7{h_sel}"
            sx = x1 + 4
            sy = y1 - 22 if y1 > 30 else y1 + 4
            self._size_id = self._canvas.create_text(
                sx, sy, text=size_text, anchor="nw",
                font=("Segoe UI", 9), fill=self._SIZE_FG,
                tags="size_label",
            )

    def _release(self, event):
        if not self._dragging or self._selection_done:
            return
        self._dragging = False

        x1, y1, x2, y2 = self._coords(event)

        if x2 - x1 < 5 or y2 - y1 < 5:
            self._cancel()
            return

        self._selection_done = True
        self._sel_coords = (x1, y1, x2, y2)
        self._captured_image = self._screenshot.crop((x1, y1, x2, y2))
        self._show_toolbar(x1, y1, x2, y2)

    # ── Floating toolbar (Lightshot-style) ──

    def _show_toolbar(self, x1, y1, x2, y2):
        btn_h = 36
        tb_w = 220
        tb_h = btn_h + 12
        pad = 8

        tb_x = x2 - tb_w
        tb_y = y2 + pad

        if tb_x < 0:
            tb_x = x1
        if tb_y + tb_h > self._sh:
            tb_y = y1 - tb_h - pad
        if tb_y < 0:
            tb_y = y2 + pad
        if tb_x + tb_w > self._sw:
            tb_x = self._sw - tb_w - pad

        self._toolbar_frame = tk.Frame(
            self.window, bg=self._TB_BG,
            highlightbackground="#3a3a4f",
            highlightthickness=1,
        )
        self._toolbar_frame.place(x=tb_x, y=tb_y, width=tb_w, height=tb_h)

        inner = tk.Frame(self._toolbar_frame, bg=self._TB_BG)
        inner.pack(expand=True, fill="both", padx=4, pady=4)

        buttons = [
            ("T", "Extract Text (OCR)", self._action_extract),
            ("\u2398", "Copy Text", self._action_copy_text),
            ("\u2B07", "Save Image", self._action_save),
            ("\u21BB", "New Capture", self._action_recapture),
            ("\u2715", "Cancel", self._cancel),
        ]

        for symbol, tip_text, cmd in buttons:
            btn = tk.Button(
                inner, text=symbol,
                font=("Segoe UI", 13),
                fg=self._TB_ICON_FG, bg=self._TB_BTN,
                activeforeground="#ffffff",
                activebackground=self._TB_BTN_HOVER,
                relief="flat", cursor="hand2",
                width=2, height=1,
                command=cmd,
            )
            btn.pack(side="left", padx=2)

            btn.bind("<Enter>", lambda e, b=btn: b.config(bg=self._TB_BTN_HOVER))
            btn.bind("<Leave>", lambda e, b=btn: b.config(bg=self._TB_BTN))

            ToolTip(btn, tip_text)

    # ── Toolbar actions ──

    def _action_extract(self):
        image = self._captured_image
        if image:
            self._cleanup()
            self._on_capture(image, "extract")

    def _action_copy_text(self):
        image = self._captured_image
        if image:
            self._cleanup()
            self._on_capture(image, "copy")

    def _action_save(self):
        image = self._captured_image
        if image:
            self._cleanup()
            self._on_capture(image, "save")

    def _action_recapture(self):
        self._cleanup()
        self._on_cancel(recapture=True)

    def _cancel(self, _event=None):
        self._cleanup()
        self._on_cancel()

    def _cleanup(self):
        self._screenshot = None
        self._dimmed = None
        self._captured_image = None
        try:
            self.window.destroy()
        except Exception:
            pass
