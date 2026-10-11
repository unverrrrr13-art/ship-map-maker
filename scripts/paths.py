from pathlib import Path


def project_root() -> Path:
    return Path(__file__).resolve().parent.parent


def images_dir() -> Path:
    return project_root() / "images"


def image_path(filename: str) -> str:
    return str(images_dir() / filename)


def output_dir() -> Path:
    d = project_root() / "output"
    d.mkdir(parents=True, exist_ok=True)
    return d


def storage_dir() -> Path:
    d = project_root() / "storage"
    d.mkdir(parents=True, exist_ok=True)
    return d


def schools_file() -> Path:
    return storage_dir() / "schools.txt"