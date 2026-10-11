import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from datetime import datetime

import config
from image_loader import load_images
from painter import ZonePainter
from canvas_view import CanvasView
from paths import output_dir
from schools import load_schools
from ui_theme import apply_theme


class InteractiveMapApp:
    def __init__(self, root):
        self.root = root
        self.root.title(config.WINDOW_TITLE)
        self.root.geometry(f"{config.WINDOW_WIDTH}x{config.WINDOW_HEIGHT}")
        self.root.minsize(config.WINDOW_MIN_WIDTH, config.WINDOW_MIN_HEIGHT)
        self.root.configure(bg=config.COLOR_BG_DARK)

        # Применяем ttk-тему до создания виджетов
        apply_theme(self.root)

        # Загрузка изображений и маски
        images = load_images()
        self.orig_img = images.orig
        self.mask_img = images.mask

        # Логика заливки
        self.painter = ZonePainter(images.orig, images.mask_array)
        self.current_paint_color = config.DEFAULT_PAINT_COLOR

        # Список школ из storage/schools.txt
        self.schools = load_schools()

        # Внутреннее состояние UI
        self._resize_job = None
        self._schools_menu = None

        self.setup_ui()
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
        panel = tk.Frame(self.root, bg=config.COLOR_BG_PANEL)
        panel.pack(side=tk.TOP, fill=tk.X)

        # Тонкая линия под панелью
        sep = tk.Frame(self.root, height=1, bg=config.COLOR_BORDER)
        sep.pack(side=tk.TOP, fill=tk.X)

        ttk.Label(
            panel,
            text="Кликните на каюту или квартал для захвата территории",
            style="App.TLabel",
        ).pack(side=tk.LEFT, padx=20, pady=10)

        ttk.Button(
            panel,
            text="Сохранить PNG",
            style="App.TButton",
            command=self.save_png,
        ).pack(side=tk.RIGHT, padx=(0, 15), pady=8)

        ttk.Button(
            panel,
            text="Сбросить всё",
            style="Secondary.TButton",
            command=self.reset_all,
        ).pack(side=tk.RIGHT, padx=(0, 8), pady=8)

    def _build_schools_button(self):
        """Кнопка внизу справа, поверх канваса."""
        self.schools_btn = ttk.Button(
            self.root,
            text="Выбрать школу",
            style="App.TButton",
            command=self.toggle_schools_menu,
        )
        self.schools_btn.place(relx=1.0, rely=1.0, anchor="se", x=-20, y=-20)

    # === МЕНЮ ШКОЛ ===

    def toggle_schools_menu(self):
        if self._schools_menu is not None:
            self._close_schools_menu()
        else:
            self._open_schools_menu()

    def _open_schools_menu(self):
        menu = tk.Frame(
            self.root,
            bg=config.COLOR_BG_MENU,
            highlightthickness=1,
            highlightbackground=config.COLOR_BORDER,
        )

        # Заголовок меню
        header = tk.Label(
            menu,
            text="Выбор школы",
            bg=config.COLOR_BG_MENU,
            fg=config.COLOR_TEXT_MUTED,
            font=("Segoe UI", 9, "bold"),
            anchor="w",
            padx=10,
            pady=6,
        )
        header.pack(fill=tk.X)

        # Разделитель под заголовком
        tk.Frame(menu, height=1, bg=config.COLOR_BORDER).pack(fill=tk.X)

        for school_name, rgb in self.schools:
            hex_color = "#{:02x}{:02x}{:02x}".format(*rgb)

            row = tk.Frame(menu, bg=config.COLOR_BG_MENU, cursor="hand2")
            row.pack(fill=tk.X)

            inner = tk.Frame(row, bg=config.COLOR_BG_MENU)
            inner.pack(fill=tk.X, padx=10, pady=6)

            swatch = tk.Frame(
                inner, width=14, height=14, bg=hex_color,
                highlightthickness=1,
                highlightbackground="#000000",
            )
            swatch.pack(side=tk.LEFT, padx=(0, 10))
            swatch.pack_propagate(False)

            lbl = tk.Label(
                inner,
                text=school_name,
                bg=config.COLOR_BG_MENU,
                fg=config.COLOR_TEXT_PRIMARY,
                font=config.FONT_UI,
                anchor="w",
            )
            lbl.pack(side=tk.LEFT, fill=tk.X, expand=True)

            # Замыкаем значения через аргументы по умолчанию,
            # чтобы каждая итерация захватила свои row/inner/lbl.
            def on_enter(e, row_w=row, inner_w=inner, lbl_w=lbl):
                for w in (row_w, inner_w, lbl_w):
                    w.configure(bg=config.COLOR_BG_MENU_HOVER)

            def on_leave(e, row_w=row, inner_w=inner, lbl_w=lbl):
                for w in (row_w, inner_w, lbl_w):
                    w.configure(bg=config.COLOR_BG_MENU)

            def on_click(e, rgb_=rgb, name_=school_name):
                self._select_school(rgb_, name_)

            for w in (row, inner, swatch, lbl):
                w.bind("<Enter>", on_enter)
                w.bind("<Leave>", on_leave)
                w.bind("<Button-1>", on_click)

        # Считаем размеры меню
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
        y = btn_y - menu_h - 8

        root_w = self.root.winfo_width()
        root_h = self.root.winfo_height()
        if x < 0:
            x = 0
        if x + menu_w > root_w:
            x = root_w - menu_w
        if y < 0:
            y = btn_y + btn_h + 8

        menu.place(x=x, y=y)
        menu.lift()

        self._schools_menu = menu
        self.root.bind("<Button-1>", self._on_root_click, add="+")

    def _on_root_click(self, event):
        if self._schools_menu is None:
            return
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