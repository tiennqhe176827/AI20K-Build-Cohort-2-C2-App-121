from __future__ import annotations

from functools import lru_cache
from pathlib import Path

from transformers import pipeline

from src.config import get_settings
from src.services.gemini_client import client
import torch

settings = get_settings()

GEMINI_MODEL = settings.gemini_model_name
ASR_MODEL = "vinai/PhoWhisper-small"


@lru_cache(maxsize=1)
def _get_transcriber():
    return pipeline(
        task="automatic-speech-recognition",
        model=ASR_MODEL,
    )


def transcribe_audio(audio_path: str) -> str:
    path = Path(audio_path)

    if not path.exists():
        raise FileNotFoundError(
            f"Không tìm thấy file âm thanh: {audio_path}"
        )

    try:
        result = _get_transcriber()(
            str(path),
            return_timestamps=True,
            chunk_length_s=30,
            generate_kwargs={
                "language": "vi",
                "task": "transcribe",
            },
        )

        text = result.get("text", "").strip()

        if not text:
            raise ValueError(
                "Không nhận diện được nội dung âm thanh"
            )

        return text

    except Exception as e:
        raise RuntimeError(
            f"Lỗi ASR: {str(e)}"
        ) from e


def fix_spelling(text: str) -> str:
    prompt = f"""
Bạn là chuyên gia hiệu đính transcript tiếng Việt từ hệ thống ASR.

Yêu cầu:
- Sửa lỗi chính tả.
- Sửa dấu câu.
- Viết hoa tên riêng nếu phù hợp.
- Giữ nguyên ý nghĩa gốc.
- Trong câu có thể xuất hiện thuật ngữ tiếng Anh.
- KHÔNG dịch thuật ngữ tiếng Anh sang tiếng Việt.
- Giữ nguyên tên sản phẩm, tên công nghệ, tên công ty, framework, API, model AI,...
- Nếu không chắc một từ là tiếng Việt hay tiếng Anh thì ưu tiên giữ nguyên.
- Không thêm nội dung mới.
- Không giải thích.
- Chỉ trả về văn bản đã hiệu đính.

Transcript:

{text}
"""

    response = client.models.generate_content(
        model=GEMINI_MODEL,
        contents=prompt,
    )

    return response.text.strip()


def convert_to_soap_note(transcript: str) -> str:
    prompt = f"""
Bạn là trợ lý Clinical Scribe cho bác sĩ.

Nhiệm vụ:
- Chuyển transcript cuộc hội thoại khám bệnh thành SOAP Note.
- Chỉ sử dụng thông tin xuất hiện trong transcript.
- Không tự ý suy diễn dữ liệu không có.
- Không tự động kết luận chẩn đoán nếu bác sĩ chưa kết luận.
- Nếu thiếu thông tin thì ghi "Chưa ghi nhận".
- Trả kết quả bằng tiếng Việt.
- Trả về đúng định dạng SOAP.

Định dạng:

# S - Subjective
(Triệu chứng, bệnh sử, than phiền của bệnh nhân)

# O - Objective
(Dấu hiệu khách quan, chỉ số, kết quả thăm khám)

# A - Assessment
(Nhận định lâm sàng dựa trên thông tin đã có)

# P - Plan
(Hướng xử trí, xét nghiệm, thuốc, theo dõi)

Transcript:

{transcript}
"""

    response = client.models.generate_content(
        model=GEMINI_MODEL,
        contents=prompt,
    )

    return response.text.strip()
