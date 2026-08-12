from pathlib import Path

import yaml

_TEXTS_DIR = Path(__file__).parent


def load(lang: str = "uz", category: str = "messages") -> dict:
    file_path = _TEXTS_DIR / lang / f"{category}.yaml"
    if not file_path.exists():
        raise FileNotFoundError(f"Tarjima fayli topilmadi: {file_path}")
    with open(file_path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)
