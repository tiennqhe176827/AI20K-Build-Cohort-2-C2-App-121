import os
import tempfile
from pathlib import Path

from src.agents.graph import clinical_agent
from src.core.logging import get_logger

logger = get_logger("api.clinical.service")

ALLOWED_AUDIO_EXTENSIONS = {".mp3", ".wav", ".m4a", ".ogg", ".flac", ".webm"}


def validate_audio_extension(filename: str | None) -> str:
    suffix = Path(filename or "").suffix.lower()
    if suffix not in ALLOWED_AUDIO_EXTENSIONS:
        allowed = ", ".join(sorted(ALLOWED_AUDIO_EXTENSIONS))
        raise ValueError(f"Định dạng không hỗ trợ. Hãy dùng: {allowed}")
    return suffix


async def process_audio_upload(file_bytes: bytes, filename: str | None) -> dict:
    suffix = validate_audio_extension(filename)

    if not file_bytes:
        raise ValueError("File âm thanh trống")

    tmp_path: str | None = None
    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
            tmp.write(file_bytes)
            tmp_path = tmp.name

        logger.info("Processing audio file: %s", filename)
        result = await clinical_agent.ainvoke({"audio_path": tmp_path})

        if result.get("error"):
            raise RuntimeError(result["error"])

        return {
            "transcript": result.get("transcript", ""),
            "corrected_transcript": result.get("corrected_transcript", ""),
            "soap_note": result.get("soap_note", ""),
        }
    finally:
        if tmp_path and os.path.exists(tmp_path):
            os.unlink(tmp_path)
