from pathlib import Path

def img_to_path(filename: str) -> Path:
    # __file__ — путь к текущему .py файлу (scripts/main.py)
    # .parent — папка scripts/
    # .parent ещё раз — корень проекта
    images_dir = Path(__file__).resolve().parent.parent / "images"
    return images_dir / filename