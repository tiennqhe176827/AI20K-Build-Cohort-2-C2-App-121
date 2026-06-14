import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent.parent))

from fastmcp import FastMCP

from src.agents.tools.clinical import (
    convert_to_soap_note as _convert_to_soap_note,
    fix_spelling as _fix_spelling,
    transcribe_audio as _transcribe_audio,
)

mcp = FastMCP("clinical-tools")


@mcp.tool()
def transcribe_audio(audio_path: str) -> str:
    """Chuyển file âm thanh khám bệnh thành transcript tiếng Việt."""
    return _transcribe_audio(audio_path)


@mcp.tool()
def fix_spelling(text: str) -> str:
    """Hiệu đính chính tả và dấu câu cho transcript ASR."""
    return _fix_spelling(text)


@mcp.tool()
def convert_to_soap_note(transcript: str) -> str:
    """Chuyển transcript khám bệnh thành SOAP note."""
    return _convert_to_soap_note(transcript)


if __name__ == "__main__":
    mcp.run(transport="http", host="0.0.0.0", port=8001)
