import tkinter as tk
from tkinter import colorchooser, filedialog, messagebox

import config
from image_loader import load_images
from painter import ZonePainter
from canvas_view import CanvasView
from paths import project_root


class InteractiveMapApp:
    def __init__(self, root):
        self.root = root
        self.root.title(config.WINDOW_TITLE)
        self.root.geometry(f"{config.WINDOW_WIDTH}x{config.WINDOW_HEIGHT}")
        self.root.minsize(config.WINDOW_MIN_WIDTH, config.WINDOW_MIN_HEIGHT)

        images = load_images()
        self.orig_img = images.orig
        self.mask_img = images.mask

        self.painter = ZonePainter(images.orig, images.mask_array)
        self.current_paint_color = config.DEFAULT_PAINT_COLOR

        self._resize_job = None

        self.setup_ui()

        # Первый рендер (уже с восстановленным состоянием)
        self.root.after(100, self._initial_render)

    def _initial_render(self):
        self.view.invalidate_cache()
        self.view.render(self.painter.display_img, force=True)

    # === ИНТЕРФЕЙС ===

    def setup_ui(self):
        self._build_control_panel()

        self.view = CanvasView(self.root)
        self.view.bind("<Configure>", self.on_canvas_resize)
        self.view.bind("<Button-1>", self.on_canvas_click)
        self.view.bind("<Button-3>", self.on_canvas_right_click)

    def _build_control_panel(self):
        panel = tk.Frame(self.root, bg=config.PANEL_BG)
        panel.pack(side=tk.TOP, fill=tk.X)

        tk.Button(
            panel, text="Выбрать цвет школы",
            command=self.choose_color,
            font=("Arial", 10, "bold"),
        ).pack(side=tk.LEFT, padx=10, pady=5)

        self.color_indicator = tk.Frame(
            panel, width=30, height=20,
            bg="#ff0000", relief=tk.SOLID, bd=1,
        )
        self.color_indicator.pack(side=tk.LEFT)

        tk.Label(
            panel,
            text="<- Кликните на каюту или квартал для захвата территории",
            bg=config.PANEL_BG, fg=config.TEXT_COLOR,
            font=("Arial", 10),
        ).pack(side=tk.LEFT, padx=20)

        tk.Button(
            panel, text="Сохранить PNG",
            command=self.save_png,
            font=("Arial", 10),
        ).pack(side=tk.LEFT, padx=10)

        tk.Button(
            panel, text="Сбросить всё",
            command=self.reset_all,
            font=("Arial", 10),
        ).pack(side=tk.LEFT)

    # === ОБРАБОТЧИКИ ===

    def on_canvas_resize(self, event):
        if self._resize_job is not None:
            self.root.after_cancel(self._resize_job)
        self._resize_job = self.root.after(80, self._do_resize_render)

    def _do_resize_render(self):
        self._resize_job = None
        self.view.invalidate_cache()
        self.view.render(self.painter.display_img, force=True)

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
        # Автосохранение после каждой покраски — чтобы ничего не потерялось
        self.painter.save_state()

        self.view.invalidate_cache()
        self.view.render(self.painter.display_img, force=True)

    def on_canvas_right_click(self, event):
        """ПКМ — снять заливку с зоны."""
        x, y = self.view.to_image_coords(event.x, event.y)
        if x is None:
            return
        if not (0 <= x < self.orig_img.width and 0 <= y < self.orig_img.height):
            return

        zone_id = self.mask_img.getpixel((x, y))
        if zone_id == (0, 0, 0):
            return

        if self.painter.erase_zone(zone_id):
            self.painter.save_state()
            self.view.invalidate_cache()
            self.view.render(self.painter.display_img, force=True)

    def choose_color(self):
        color_code = colorchooser.askcolor(title="Выберите цвет фракции")
        if color_code[0]:
            r, g, b = map(int, color_code[0])
            self.current_paint_color = (r, g, b, config.ACTIVE_ALPHA)
            self.color_indicator.config(bg=color_code[1])

    # === СОХРАНЕНИЕ PNG ===

    def save_png(self):
        default_dir = project_root()
        filepath = filedialog.asksaveasfilename(
            title="Сохранить карту как PNG",
            initialdir=str(default_dir),
            defaultextension=".png",
            filetypes=[("PNG", "*.png"), ("Все файлы", "*.*")],
            initialfile="map_result.png",
        )
        if not filepath:
            return

        try:
            # display_img уже в оригинальном разрешении
            self.painter.display_img.save(filepath, "PNG")
            messagebox.showinfo("Готово", f"Карта сохранена:\n{filepath}")
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось сохранить:\n{e}")

    # === СБРОС ===

    def reset_all(self):
        if not messagebox.askyesno(
            "Сброс",
            "Убрать все заливки? Это действие нельзя отменить.",
        ):
            return
        self.painter.reset()
        self.view.invalidate_cache()
        self.view.render(self.painter.display_img, force=True)