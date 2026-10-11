from pathlib import Path


def project_root() -> Path:
    """Корень проекта (папка, где лежат scripts/, images/)."""
    return Path(__file__).resolve().parent.parent


def images_dir() -> Path:
    return project_root() / "images"


def image_path(filename: str) -> str:
    """Полный путь к файлу в images/ в виде строки."""
    return str(images_dir() / filename)


def output_dir() -> Path:
    """Папка для сохранённых карт. Создаётся автоматически при первом обращении."""
    d = project_root() / "output"
    d.mkdir(parents=True, exist_ok=True)
    return d