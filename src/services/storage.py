import os
from pathlib import Path

from src.core.logging import get_logger

logger = get_logger("services.storage")

UPLOAD_DIR = Path("data/uploads")
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)


def save_upload(file_bytes: bytes, filename: str, subdir: str = "") -> str:
    target_dir = UPLOAD_DIR / subdir if subdir else UPLOAD_DIR
    target_dir.mkdir(parents=True, exist_ok=True)

    file_path = target_dir / filename
    file_path.write_bytes(file_bytes)

    logger.info("Saved upload: %s", file_path)
    return str(file_path)


def delete_upload(file_path: str) -> bool:
    try:
        os.unlink(file_path)
        logger.info("Deleted upload: %s", file_path)
        return True
    except FileNotFoundError:
        return False


def get_upload_path(filename: str, subdir: str = "") -> Path:
    target_dir = UPLOAD_DIR / subdir if subdir else UPLOAD_DIR
    return target_dir / filename
