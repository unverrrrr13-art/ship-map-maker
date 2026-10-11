from pathlib import Path

def project_root() -> Path:
    """Корень проекта (папка, где лежат scripts/, images/ и т.д.)."""
    return Path(__file__).resolve().parent.parent

def images_dir() -> Path:
    return project_root() / "images"

def image_path(filename: str) -> str:
    """Полный путь к файлу в папке images/ в виде строки."""
    return str(images_dir() / filename)