from pathlib import Path


def normalize(path):
    return Path(path).read_text(encoding="utf-8").strip().lower()
