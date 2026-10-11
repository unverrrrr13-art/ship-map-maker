from tkinter import ttk
import config


def apply_theme(root):
    """
    Настраивает ttk-стили под нашу палитру.
    Вызывать один раз после создания root, до создания виджетов.
    """
    style = ttk.Style(root)

    # clam — самая нейтральная из встроенных тем,
    # легко перекрашивается
    try:
        style.theme_use("clam")
    except Exception:
        pass

    # --- Базовая кнопка ---
    style.configure(
        "App.TButton",
        font=config.FONT_BUTTON,
        padding=(14, 8),
        relief="flat",
        borderwidth=0,
        background=config.COLOR_BG_BUTTON,
        foreground=config.COLOR_TEXT_ON_BTN,
        focuscolor=config.COLOR_BG_BUTTON,
    )
    style.map(
        "App.TButton",
        background=[
            ("active", config.COLOR_BG_BUTTON_HOVER),
            ("pressed", config.COLOR_BG_BUTTON_HOVER),
        ],
        foreground=[("active", config.COLOR_TEXT_ON_BTN)],
    )

    # --- Вторичная кнопка (для «Сбросить») ---
    style.configure(
        "Secondary.TButton",
        font=config.FONT_BUTTON,
        padding=(12, 7),
        relief="flat",
        borderwidth=0,
        background=config.COLOR_BG_PANEL,
        foreground=config.COLOR_TEXT_PRIMARY,
    )
    style.map(
        "Secondary.TButton",
        background=[
            ("active", config.COLOR_BORDER),
            ("pressed", config.COLOR_BORDER),
        ],
    )

    # --- Метка ---
    style.configure(
        "App.TLabel",
        background=config.COLOR_BG_PANEL,
        foreground=config.COLOR_TEXT_PRIMARY,
        font=config.FONT_UI,
    )

    # --- Разделитель ---
    style.configure(
        "App.TSeparator",
        background=config.COLOR_BORDER,
    )

    return style