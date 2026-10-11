import tkinter as tk
from tkinter import colorchooser
from PIL import Image, ImageTk, ImageDraw
import path

# === НАСТРОЙКИ ФАЙЛОВ ===
# Укажите пути к вашим изображениям (они должны быть в одной папке со скриптом)
IMAGE = "ship_main.png" 
MASK = "ship_mask.png" 

IMAGE_PATH = path.img_to_path(IMAGE)     # Исходное красивое изображение корабля
MASK_PATH = path.img_to_path(MASK)     # Карта-маска, где каждая комната залита своим уникальным цветом

class InteractiveMapApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Girls und Panzer: Школьный Авианосец — Захват Территорий")

        # Загружаем оригинальное изображение и маску
        self.orig_img = Image.open(IMAGE_PATH).convert("RGBA")
        self.mask_img = Image.open(MASK_PATH).convert("RGB")
        
        if self.orig_img.size != self.mask_img.size:
            print("Внимание: Размеры основного изображения и маски должны строго совпадать!")

        # Создаем копию для динамического рисования поверх нее
        self.display_img = self.orig_img.copy()
        
        # Текущий цвет фракции/школы для покраски (по умолчанию красный)
        self.current_paint_color = (255, 0, 0, 128) # Полупрозрачный красный

        # Настраиваем интерфейс Tkinter
        self.setup_ui()

    def setup_ui(self):
        # Панель управления сверху
        control_panel = tk.Frame(self.root, bg="#2c3e50", padding=10)
        control_panel.pack(side=tk.TOP, fill=tk.X)

        color_btn = tk.Button(control_panel, text="Выбрать цвет школы", command=self.choose_color, font=("Arial", 10, "bold"))
        color_btn.pack(side=tk.LEFT, padx=10)

        self.color_indicator = tk.Frame(control_panel, width=30, height=20, bg="#ff0000", relief=tk.SOLID, bd=1)
        self.color_indicator.pack(side=tk.LEFT)

        info_label = tk.Label(control_panel, text="<- Кликните на каюту или квартал для захвата территории", bg="#2c3e50", fg="white", font=("Arial", 10))
        info_label.pack(side=tk.LEFT, padx=20)

        # Область скроллинга на случай, если картинка больше экрана
        self.canvas = tk.Canvas(self.root, width=1200, height=600, bg="grey")
        self.canvas.pack(fill=tk.BOTH, expand=True)

        # Выводим картинку на холст
        self.tk_img = ImageTk.PhotoImage(self.display_img)
        self.image_on_canvas = self.canvas.create_image(0, 0, anchor=tk.NW, image=self.tk_img)

        # Привязываем клик мыши
        self.canvas.bind("<Button-1>", self.on_canvas_click)

    def choose_color(self):
        # Окно выбора цвета для захватывающей школы
        color_code = colorchooser.askcolor(title="Выберите цвет фракции")
        if color_code[0]:
            r, g, b = map(int, color_code[0])
            self.current_paint_color = (r, g, b, 140) # 140 — уровень прозрачности (Alpha)
            self.color_indicator.config(bg=color_code[1])

    def on_canvas_click(self, event):
        # Получаем координаты клика на холсте
        x = self.canvas.canvasx(event.x)
        y = self.canvas.canvasy(event.y)

        # Проверяем, что клик в пределах картинки
        if 0 <= x < self.orig_img.width and 0 <= y < self.orig_img.height:
            # Определяем уникальный ID-цвет зоны по маске
            target_zone_id = self.mask_img.getpixel((int(x), int(y)))
            
            # Если кликнули в черный цвет (границы или фон), ничего не делаем
            if target_zone_id == (0, 0, 0):
                return
            
            # Запускаем заливку зоны
            self.flood_fill_zone(target_zone_id)

    def flood_fill_zone(self, zone_id):
        # Создаем маску закрашиваемой зоны
        width, height = self.mask_img.width, self.mask_img.height
        
        # Оптимизированный поиск пикселей этой зоны и их перекраска с альфа-слоем
        overlay = Image.new("RGBA", (width, height), (0, 0, 0, 0))
        draw = ImageDraw.Draw(overlay)

        # Проходимся по пикселям (для ускорения в больших проектах зоны обычно кэшируют, 
        # но для прототипа достаточно прямого попиксельного сравнения)
        mask_pixels = self.mask_img.load()
        for y in range(height):
            for x in range(width):
                if mask_pixels[x, y] == zone_id:
                    draw.point((x, y), fill=self.current_paint_color)

        # Накладываем измененную область поверх оригинального корабля
        self.display_img = Image.alpha_composite(self.orig_img.convert("RGBA"), overlay)
        
        # Обновляем картинку в интерфейсе
        self.tk_img = ImageTk.PhotoImage(self.display_img)
        self.canvas.itemconfig(self.image_on_canvas, image=self.tk_img)

if __name__ == "__main__":
    root = tk.Tk()
    app = InteractiveMapApp(root)
    root.mainloop()