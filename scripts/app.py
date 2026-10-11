import tkinter as tk
from tkinter import colorchooser

import config
from image_loader import load_images
from painter import ZonePainter
from canvas_view import CanvasView


class InteractiveMapApp:
    def __init__(self, root):
        self.root = root
        self.root.title(config.WINDOW_TITLE)
        self.root.geometry(f"{config.WINDOW_WIDTH}x{config.WINDOW_HEIGHT}")
        self.root.minsize(config.WINDOW_MIN_WIDTH, config.WINDOW_MIN_HEIGHT)

        # Загрузка
        images = load_images()
        self.orig_img = images.orig
        self.mask_img = images.mask

        # Логика заливки
        self.painter = ZonePainter(images.orig, images.mask_array)

        # Текущий цвет фракции
        self.current_paint_color = config.DEFAULT_PAINT_COLOR

        self.setup_ui()

    def setup_ui(self):
        self._build_control_panel()

        self.view = CanvasView(self.root)
        self.view.bind("<Configure>", self.on_canvas_resize)
        self.view.bind("<Button-1>", self.on_canvas_click)

    def _build_control_panel(self):
        panel = tk.Frame(self.root, bg=config.PANEL_BG)
        panel.pack(side=tk.TOP, fill=tk.X)

        tk.Button(panel, text="Выбрать цвет школы",
                  command=self.choose_color,
                  font=("Arial", 10, "bold")) \
            .pack(side=tk.LEFT, padx=10, pady=5)

        self.color_indicator = tk.Frame(panel, width=30, height=20,
                                        bg="#ff0000", relief=tk.SOLID, bd=1)
        self.color_indicator.pack(side=tk.LEFT)

        tk.Label(panel,
                 text="<- Кликните на каюту или квартал для захвата территории",
                 bg=config.PANEL_BG, fg=config.TEXT_COLOR,
                 font=("Arial", 10)) \
            .pack(side=tk.LEFT, padx=20)

    # === ОБРАБОТЧИКИ ===

    def on_canvas_resize(self, event):
        self.view.render(self.painter.display_img)

    def on_canvas_click(self, event):
        x, y = self.view.to_image_coords(event.x, event.y)
        if x is None:
            return

        if not (0 <= x < self.orig_img.width and 0 <= y < self.orig_img.height):
            return

        zone_id = self.mask_img.getpixel((x, y))
        if zone_id == (0, 0, 0):
            return

        self.painter.paint_zone(zone_id, self.current_paint_color)
        self.view.render(self.painter.display_img)

    def choose_color(self):
        color_code = colorchooser.askcolor(title="Выберите цвет фракции")
        if color_code[0]:
            r, g, b = map(int, color_code[0])
            self.current_paint_color = (r, g, b, config.ACTIVE_ALPHA)
            self.color_indicator.config(bg=color_code[1])