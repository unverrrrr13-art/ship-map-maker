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
# Тёмно-синяя гамма (что-то вроде «night blue»)
COLOR_BG_DARK      = "#1b2430"   # фон верхней панели / root
COLOR_BG_PANEL     = "#232f3e"   # фон панели управления
COLOR_BG_CANVAS    = "#2b3648"   # фон канваса (за картинкой)
COLOR_BG_MENU      = "#232f3e"   # фон меню школ
COLOR_BG_MENU_HOVER = "#2f3d51"  # фон строки меню при наведении
COLOR_BG_BUTTON    = "#3b82f6"   # основной цвет кнопки
COLOR_BG_BUTTON_HOVER = "#2563eb"

COLOR_TEXT_PRIMARY = "#e8edf2"   # основной текст
COLOR_TEXT_MUTED   = "#9aa7b8"   # вторичный текст
COLOR_TEXT_ON_BTN  = "#ffffff"

COLOR_BORDER       = "#3a4a5e"   # тонкие рамки/разделители

# === ШРИФТЫ ===
FONT_UI        = ("Segoe UI", 10)
FONT_UI_BOLD   = ("Segoe UI", 10, "bold")
FONT_TITLE     = ("Segoe UI", 11, "bold")
FONT_BUTTON    = ("Segoe UI", 10, "bold")

# === ЗАЛИВКА ===
DEFAULT_PAINT_COLOR = (255, 0, 0, 128)
ACTIVE_ALPHA = 140

# === АЛИАСЫ ДЛЯ СОВМЕСТИМОСТИ ===
# Старые имена, которые могут использоваться в других модулях
CANVAS_BG = COLOR_BG_CANVAS
PANEL_BG = COLOR_BG_PANEL
TEXT_COLOR = COLOR_TEXT_PRIMARY