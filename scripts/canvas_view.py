import tkinter as tk
from PIL import Image, ImageTk

import config


class CanvasView:
    def __init__(self, parent):
        self.canvas = tk.Canvas(parent, bg=config.CANVAS_BG, highlightthickness=0)
        self.canvas.pack(fill=tk.BOTH, expand=True)

        self.image_on_canvas = self.canvas.create_image(0, 0, anchor=tk.NW)

        self.tk_img = None
        self.scale = 1.0
        self.offset_x = 0
        self.offset_y = 0

    def render(self, display_img: Image.Image):
        """Масштабирует display_img под размер канваса и рисует."""
        cw = self.canvas.winfo_width()
        ch = self.canvas.winfo_height()
        if cw <= 1 or ch <= 1:
            return

        ow, oh = display_img.size
        self.scale = min(cw / ow, ch / oh)

        new_w = max(1, int(ow * self.scale))
        new_h = max(1, int(oh * self.scale))

        resized = display_img.resize((new_w, new_h), Image.LANCZOS)
        self.tk_img = ImageTk.PhotoImage(resized)

        self.offset_x = (cw - new_w) // 2
        self.offset_y = (ch - new_h) // 2

        self.canvas.itemconfig(self.image_on_canvas, image=self.tk_img)
        self.canvas.coords(self.image_on_canvas, self.offset_x, self.offset_y)

    def to_image_coords(self, event_x: int, event_y: int):
        """Переводит координаты клика в координаты оригинала картинки."""
        if self.scale <= 0:
            return None, None
        x = int((event_x - self.offset_x) / self.scale)
        y = int((event_y - self.offset_y) / self.scale)
        return x, y

    def bind(self, event: str, handler):
        self.canvas.bind(event, handler)