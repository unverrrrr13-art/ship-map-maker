import time
import tkinter as tk
from PIL import Image, ImageTk

import config


class CanvasView:
    def __init__(self, parent):
        self.canvas = tk.Canvas(parent, bg=config.CANVAS_BG, highlightthickness=0)
        self.canvas.pack(fill=tk.BOTH, expand=True)

        self.image_on_canvas = self.canvas.create_image(0, 0, anchor=tk.NW)

        self.tk_img = None
        self.base_scale = 1.0
        self.offset_x = 0
        self.offset_y = 0

        self._last_render_key = None
        self._last_render_time = 0.0
        self._pending_render = None

    # === ОТРИСОВКА ===

    def render(self, display_img: Image.Image, force: bool = False):
        cw = self.canvas.winfo_width()
        ch = self.canvas.winfo_height()
        if cw <= 1 or ch <= 1:
            return

        key = (id(display_img), cw, ch)
        if not force and key == self._last_render_key:
            return

        now = time.perf_counter()
        if not force and (now - self._last_render_time) < 0.016:
            self._schedule_render(display_img)
            return

        self._last_render_key = key
        self._last_render_time = now

        ow, oh = display_img.size
        self.base_scale = min(cw / ow, ch / oh)

        new_w = max(1, int(ow * self.base_scale))
        new_h = max(1, int(oh * self.base_scale))

        resized = display_img.resize((new_w, new_h), Image.BILINEAR)
        self.tk_img = ImageTk.PhotoImage(resized)

        self.offset_x = (cw - new_w) // 2
        self.offset_y = (ch - new_h) // 2

        self.canvas.itemconfig(self.image_on_canvas, image=self.tk_img)
        self.canvas.coords(self.image_on_canvas, self.offset_x, self.offset_y)

    def _schedule_render(self, display_img):
        if self._pending_render is not None:
            self.canvas.after_cancel(self._pending_render)
        self._pending_render = self.canvas.after(
            16, lambda: self._do_pending_render(display_img)
        )

    def _do_pending_render(self, display_img):
        self._pending_render = None
        self.render(display_img, force=True)

    def invalidate_cache(self):
        self._last_render_key = None

    # === ПЕРЕВОД КООРДИНАТ ===

    def to_image_coords(self, event_x: int, event_y: int):
        if self.base_scale <= 0:
            return None, None
        x = int((event_x - self.offset_x) / self.base_scale)
        y = int((event_y - self.offset_y) / self.base_scale)
        return x, y

    # === ПРИВЯЗКИ ===

    def bind(self, event: str, handler):
        self.canvas.bind(event, handler)

    def cancel_pending(self):
        if self._pending_render is not None:
            self.canvas.after_cancel(self._pending_render)
            self._pending_render = None