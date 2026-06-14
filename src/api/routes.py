import os
import tempfile

from fastapi import APIRouter, HTTPException, UploadFile


from src.models.schemas import ChatRequest, ChatResponse

from pathlib import Path
from fastapi import APIRouter, File, HTTPException, UploadFile

from src.agents.graph import clinical_agent
from src.models.schemas import ClinicalSoapResponse


router = APIRouter()


# @router.post("/chat", response_model=ChatResponse)
# async def chat(request: ChatRequest) -> ChatResponse:
#     """Chat với AI agent."""
#     try:
#         result = await agent.ainvoke({"query": request.message})
#         return ChatResponse(
#             response=result.get("response", ""),
#             analysis=result.get("analysis", ""),
#         )
#     except Exception as e:
#         raise HTTPException(status_code=500, detail=str(e))
# 
# 
# @router.get("/status")
# async def agent_status():
#     """Kiểm tra trạng thái agent."""
#     return {"status": "ready", "agent": "LangGraph Agent v1.0"}

ALLOWED_AUDIO_EXTENSIONS = {".mp3", ".wav", ".m4a", ".ogg", ".flac", ".webm"}


@router.post("/clinical/soap-note", response_model=ClinicalSoapResponse)
async def create_soap_note(file: UploadFile = File(...)) -> ClinicalSoapResponse:
    """Nhận file âm thanh khám bệnh và trả về SOAP note."""
    suffix = Path(file.filename or "").suffix.lower()
    if suffix not in ALLOWED_AUDIO_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail=f"Định dạng không hỗ trợ. Hãy dùng: {', '.join(sorted(ALLOWED_AUDIO_EXTENSIONS))}",
        )

    content = await file.read()
    if not content:
        raise HTTPException(status_code=400, detail="File âm thanh trống")

    tmp_path: str | None = None
    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
            tmp.write(content)
            tmp_path = tmp.name

        result = await clinical_agent.ainvoke({"audio_path": tmp_path})

        if result.get("error"):
            raise HTTPException(status_code=500, detail=result["error"])

        return ClinicalSoapResponse(
            transcript=result.get("transcript", ""),
            corrected_transcript=result.get("corrected_transcript", ""),
            soap_note=result.get("soap_note", ""),
        )
    except HTTPException:
        raise
    except (Exception, BaseExceptionGroup) as e:
        raise HTTPException(status_code=500, detail=str(e)) from e
    finally:
        if tmp_path and os.path.exists(tmp_path):
            os.unlink(tmp_path)


@router.get("/status")
async def agent_status():
    """Kiểm tra trạng thái agent."""
    return {
        "status": "ready",
        "agent": "Clinical LangGraph Agent v1.0",
        "pipeline": ["transcribe", "fix_spelling", "soap"],
    }
