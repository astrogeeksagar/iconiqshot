import tkinter as tk


class ToolTip:
    """Hover tooltip for any Tkinter widget. Lightweight, no extra windows."""

    def __init__(self, widget, text, bg="#2b2b3c", fg="#e0e0ef",
                 font=("Segoe UI", 9), delay=350):
        self._widget = widget
        self._text = text
        self._bg = bg
        self._fg = fg
        self._font = font
        self._delay = delay
        self._tip_window = None
        self._after_id = None

        widget.bind("<Enter>", self._schedule, add="+")
        widget.bind("<Leave>", self._hide, add="+")
        widget.bind("<ButtonPress>", self._hide, add="+")

    def _schedule(self, _event=None):
        self._cancel()
        self._after_id = self._widget.after(self._delay, self._show)

    def _cancel(self):
        if self._after_id:
            self._widget.after_cancel(self._after_id)
            self._after_id = None

    def _show(self):
        if self._tip_window:
            return
        x = self._widget.winfo_rootx() + self._widget.winfo_width() // 2
        y = self._widget.winfo_rooty() + self._widget.winfo_height() + 4

        self._tip_window = tw = tk.Toplevel(self._widget)
        tw.wm_overrideredirect(True)
        tw.wm_attributes("-topmost", True)

        label = tk.Label(
            tw, text=self._text,
            font=self._font,
            fg=self._fg, bg=self._bg,
            relief="solid", borderwidth=1,
            padx=8, pady=4,
        )
        label.pack()

        tw.update_idletasks()
        tw_w = tw.winfo_width()
        tw.wm_geometry(f"+{x - tw_w // 2}+{y}")

    def _hide(self, _event=None):
        self._cancel()
        if self._tip_window:
            self._tip_window.destroy()
            self._tip_window = None
