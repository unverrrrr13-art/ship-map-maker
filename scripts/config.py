# === ФАЙЛЫ ===
IMAGE = "ship_main.png"
MASK = "ship_mask.png"

# === ОКНО ===
WINDOW_TITLE = "Girls und Panzer: Школьный Авианосец — Захват Территорий"
WINDOW_WIDTH = 1280
WINDOW_HEIGHT = 720
WINDOW_MIN_WIDTH = 640
WINDOW_MIN_HEIGHT = 480

# === ЦВЕТОВАЯ СХЕМА ===
# Тёмно-синяя гамма
COLOR_BG_DARK         = "#1b2430"   # фон root-окна
COLOR_BG_PANEL        = "#232f3e"   # фон панели управления
COLOR_BG_CANVAS       = "#2b3648"   # фон канваса
COLOR_BG_MENU         = "#232f3e"   # фон меню школ
COLOR_BG_MENU_HOVER   = "#2f3d51"   # фон строки меню при наведении
COLOR_BG_BUTTON       = "#3b82f6"   # основная кнопка
COLOR_BG_BUTTON_HOVER = "#2563eb"   # основная кнопка при наведении

COLOR_TEXT_PRIMARY    = "#e8edf2"   # основной текст
COLOR_TEXT_MUTED      = "#9aa7b8"   # вторичный текст (заголовки меню)
COLOR_TEXT_ON_BTN     = "#ffffff"   # текст на акцентной кнопке

COLOR_BORDER          = "#3a4a5e"   # тонкие рамки/разделители

# Индикатор сохранения
COLOR_SAVE_OK   = "#22c55e"   # зелёный — успех
COLOR_SAVE_ERR  = "#ef4444"   # красный — ошибка
COLOR_SAVE_BUSY = "#f59e0b"   # янтарный — процесс идёт
SAVE_INDICATOR_DURATION = 1500   # мс, сколько держать надпись после завершения

# === ШРИФТЫ ===
# Segoe UI есть на Windows и обычно на Linux через шрифты от MS.
# Если его нет — Tk возьмёт первый доступный из семейства.
# Альтернатива для чистого Arch: "DejaVu Sans".
FONT_UI        = ("Segoe UI", 10)
FONT_UI_BOLD   = ("Segoe UI", 10, "bold")
FONT_TITLE     = ("Segoe UI", 11, "bold")
FONT_BUTTON    = ("Segoe UI", 10, "bold")

# === ЗАЛИВКА ===
DEFAULT_PAINT_COLOR = (255, 0, 0, 128)   # RGBA по умолчанию
ACTIVE_ALPHA        = 140                 # альфа при выборе цвета школы

# === АЛИАСЫ ДЛЯ СОВМЕСТИМОСТИ ===
# Старые имена, которые могут использоваться в других модулях
CANVAS_BG  = COLOR_BG_CANVAS
PANEL_BG   = COLOR_BG_PANEL
TEXT_COLOR = COLOR_TEXT_PRIMARY

# Анимация затухания индикатора
SAVE_INDICATOR_FADE_MS = 600    # длительность затухания в мс
SAVE_INDICATOR_FADE_STEP_MS = 16  # шаг кадров (~60 FPS)