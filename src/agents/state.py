from __future__ import annotations

from typing import TypedDict, Optional

#
# class AgentState(TypedDict, total=False):
#     """State schema cho LangGraph agent.
#
#     Mỗi node đọc và ghi vào state này.
#     total=False cho phép tất cả fields là optional.
#     """
#
#     query: str
#     context: str
#     analysis: str
#     response: str
#     error: str
#     metadata: dict

class ClinicalState(TypedDict, total=False):
    audio_path: str
    transcript: Optional[str]
    corrected_transcript: Optional[str]
    soap_note: Optional[str]
    current_step: Optional[str]
    error: Optional[str]
