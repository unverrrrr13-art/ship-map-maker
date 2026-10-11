from pathlib import Path
from PIL import ImageColor

from paths import schools_file


DEFAULT_SCHOOLS = [
    ("Анцио", "eeff00"),
    ("Би-Си Свобода", "3180b5"),
    ("Беллволл", "b9780f"),
    ("Чи-Ха-Тан", "22874e"),
    ("Каунт", "8a7517"),
    ("Яткосота", "a3cfd2"),
    ("Коала Форест", "233d8f"),
    ("Куроморимине", "121110"),
    ("Мажино", "030381"),
    ("Правда", "f70101"),
    ("Сандерс", "0c3611"),
    ("Святая Глориана", "201e2f"),
    ("Викинг Фишериз", "969c44"),
    ("Гаочжун Ли Хуа", "f8ea04"),
    ("Татенаси", "690306"),
]


def parse_hex(color_hex: str):
    """
    'ff0000' -> (255, 0, 0)
    Бросает ValueError при некорректном вводе.
    """
    color_hex = color_hex.strip().lstrip("#")
    if len(color_hex) != 6:
        raise ValueError(f"Ожидается 6 hex-символов, получено: {color_hex!r}")
    return tuple(int(color_hex[i:i + 2], 16) for i in (0, 2, 4))


def load_schools():
    path = schools_file()
    if not path.is_file():
        save_schools(DEFAULT_SCHOOLS)
        return [(name, parse_hex(h)) for name, h in DEFAULT_SCHOOLS]

    schools = []
    with open(path, "r", encoding="utf-8") as f:
        for lineno, raw in enumerate(f, 1):
            line = raw.strip()
            if not line or line.startswith("#"):
                continue
            if ":" not in line:
                print(f"schools.txt:{lineno}: нет ':' — пропущено: {line!r}")
                continue
            name, hex_color = line.split(":", 1)
            name = name.strip()
            try:
                rgb = parse_hex(hex_color)
            except ValueError as e:
                print(f"schools.txt:{lineno}: {e}")
                continue
            schools.append((name, rgb))
    return schools


def save_schools(schools):
    path = schools_file()
    with open(path, "w", encoding="utf-8") as f:
        for name, value in schools:
            if isinstance(value, str):
                hex_color = value.lstrip("#")
            else:
                r, g, b = value
                hex_color = f"{r:02x}{g:02x}{b:02x}"
            f.write(f"{name}:{hex_color}\n")