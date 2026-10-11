from pathlib import Path
from PIL import ImageColor

from paths import schools_file


DEFAULT_SCHOOLS = [
    ("Команда старшей школы Анцио", "f2be4c"),
    ("Взвод Пятой республики", "4b78b0"),
    ("Старшая школа Грегора", "7f6000"),
    ("Команда школы Бонпле", "ffffff"),
    ("Команда Академии Чи-Ха-Тан", "7c9c58"),
    ("Старшая школа Татегото", "006e3b"),
    ("Команда Гая Фокса", "7f7d7d"),
    ("Боевая группа Шварцвальда", "dd0000"),
    ("Старшая школа Кебаб", "bf8f6e"),
    ("Старшая школа Мейпл", "5d3229"),
    ("Добровольческая армия Катюши", "6b0000"),
    ("Добровольческая группа \"Летающие танкистки\"", "1d1309"),
    ("Чиндиты", "183B61"),
    ("Старшая школа Вигген", "a5e4ff"),
    ("Команда \"Многоножка\"", "b94545"),
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