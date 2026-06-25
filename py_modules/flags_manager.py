import os
from pathlib import Path

APP_NAME = "WebPlatform"
FLAGS_FILE_NAME = "DefWPExts.txt"

def get_flags_file_path() -> Path:
    home = Path.home()
    app_dir = home / f".{APP_NAME}"
    app_dir.mkdir(exist_ok=True)
    return app_dir / FLAGS_FILE_NAME

def load_flags() -> set[str]:
    path = get_flags_file_path()
    if not path.exists():
        return set()
    with path.open("r", encoding="utf-8") as f:
        return {line.strip() for line in f if line.strip()}

def save_flags(flags: set[str]) -> None:
    path = get_flags_file_path()
    with path.open("w", encoding="utf-8") as f:
        for flag in sorted(flags):
            f.write(flag + "\n")
