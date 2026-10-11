import tkinter as tk
from tkinter import filedialog, messagebox
from datetime import datetime

import config
from image_loader import load_images
from painter import ZonePainter
from canvas_view import CanvasView
from paths import output_dir
from schools import load_schools


class InteractiveMapApp:
    def __init__(self, root):
        self.root = root
        self.root.title(config.WINDOW_TITLE)
        self.root.geometry(f"{config.WINDOW_WIDTH}x{config.WINDOW_HEIGHT}")
        self.root.minsize(config.WINDOW_MIN_WIDTH, config.WINDOW_MIN_HEIGHT)

        # Загрузка изображений и маски
        images = load_images()
        self.orig_img = images.orig
        self.mask_img = images.mask

        # Логика заливки
        self.painter = ZonePainter(images.orig, images.mask_array)
        self.current_paint_color = config.DEFAULT_PAINT_COLOR

        # Список школ из storage/schools.txt
        self.schools = load_schools()   # [(name, (r,g,b)), ...]

        # Внутреннее состояние UI
        self._resize_job = None
        self._schools_menu = None       # ссылка на открытое меню (Frame)

        self.setup_ui()

        # Первый рендер — после того, как окно получит реальные размеры
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

        self._build_schools_button()

    def _build_control_panel(self):
        panel = tk.Frame(self.root, bg=config.PANEL_BG)
        panel.pack(side=tk.TOP, fill=tk.X)

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

    def _build_schools_button(self):
        """Кнопка внизу справа, поверх канваса."""
        self.schools_btn = tk.Button(
            self.root,
            text="Выбрать школу",
            font=("Arial", 10, "bold"),
            command=self.toggle_schools_menu,
        )
        self.schools_btn.place(relx=1.0, rely=1.0, anchor="se", x=-15, y=-15)

    # === МЕНЮ ШКОЛ ===

    def toggle_schools_menu(self):
        if self._schools_menu is not None:
            self._close_schools_menu()
        else:
            self._open_schools_menu()

    def _open_schools_menu(self):
        # Меню — Frame внутри root, чтобы координаты считались в его системе
        menu = tk.Frame(self.root, bg="#222222", bd=1, relief=tk.SOLID)

        for name, rgb in self.schools:
            row = tk.Frame(menu, bg="#222222")
            row.pack(fill=tk.X, padx=6, pady=2)

            hex_color = "#{:02x}{:02x}{:02x}".format(*rgb)

            swatch = tk.Frame(row, width=16, height=16, bg=hex_color,
                              relief=tk.SOLID, bd=1)
            swatch.pack(side=tk.LEFT, padx=(0, 8))
            swatch.pack_propagate(False)

            lbl = tk.Label(row, text=name, bg="#222222", fg="white",
                           font=("Arial", 10), anchor="w")
            lbl.pack(side=tk.LEFT, fill=tk.X, expand=True)

            for w in (row, swatch, lbl):
                w.bind("<Button-1>",
                       lambda e, r=rgb, n=name: self._select_school(r, n))

        # Считаем реальные размеры меню
        menu.update_idletasks()
        menu_w = menu.winfo_reqwidth()
        menu_h = menu.winfo_reqheight()

        # Координаты кнопки относительно root
        btn_x = self.schools_btn.winfo_x()
        btn_y = self.schools_btn.winfo_y()
        btn_w = self.schools_btn.winfo_width()
        btn_h = self.schools_btn.winfo_height()

        # Меню над кнопкой, правые края выровнены
        x = btn_x + btn_w - menu_w
        y = btn_y - menu_h - 6

        # Не вылезаем за окно
        root_w = self.root.winfo_width()
        root_h = self.root.winfo_height()
        if x < 0:
            x = 0
        if x + menu_w > root_w:
            x = root_w - menu_w
        if y < 0:
            y = btn_y + btn_h + 6

        menu.place(x=x, y=y, width=menu_w, height=menu_h)
        menu.lift()

        self._schools_menu = menu

        # Клик мимо меню — закрыть (add='+' — не перебиваем другие привязки)
        self.root.bind("<Button-1>", self._on_root_click, add="+")

    def _on_root_click(self, event):
        if self._schools_menu is None:
            return

        # Проверяем, принадлежит ли клик меню или кнопке
        w = event.widget
        while w is not None:
            if w is self._schools_menu or w is self.schools_btn:
                return
            w = getattr(w, "master", None)

        self._close_schools_menu()

    def _close_schools_menu(self):
        if self._schools_menu is not None:
            self._schools_menu.destroy()
            self._schools_menu = None
        self.root.unbind("<Button-1>")

    def _select_school(self, rgb, name):
        r, g, b = rgb
        self.current_paint_color = (r, g, b, config.ACTIVE_ALPHA)
        self.schools_btn.config(text=f"Школа: {name}")
        self._close_schools_menu()

    # === ОБРАБОТЧИКИ КАНВАСА ===

    def on_canvas_resize(self, event):
        if self._resize_job is not None:
            self.root.after_cancel(self._resize_job)
        self._resize_job = self.root.after(80, self._do_resize_render)

    def _do_resize_render(self):
        self._resize_job = None
        self.view.invalidate_cache()
        self.view.render(self.painter.display_img, force=True)

    def on_canvas_click(self, event):
        """ЛКМ — покрасить зону текущим цветом."""
        x, y = self.view.to_image_coords(event.x, event.y)
        if x is None:
            return
        if not (0 <= x < self.orig_img.width and 0 <= y < self.orig_img.height):
            return

        zone_id = self.mask_img.getpixel((x, y))
        if zone_id == (0, 0, 0):
            return

        self.painter.paint_zone(zone_id, self.current_paint_color)
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

    # === СОХРАНЕНИЕ PNG ===

    def save_png(self):
        timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        default_name = f"map_{timestamp}.png"

        filepath = filedialog.asksaveasfilename(
            title="Сохранить карту как PNG",
            initialdir=str(output_dir()),
            defaultextension=".png",
            filetypes=[("PNG", "*.png"), ("Все файлы", "*.*")],
            initialfile=default_name,
        )
        if not filepath:
            return

        try:
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