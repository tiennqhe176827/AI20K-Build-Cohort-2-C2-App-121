from fastapi import APIRouter

from src.config import get_settings

router = APIRouter(tags=["Health"])


@router.get("/status")
async def agent_status() -> dict:
    """Kiểm tra trạng thái agent."""
    settings = get_settings()
    return {
        "status": "ready",
        "agent": "Clinical LangGraph Agent v1.0",
        "pipeline": ["transcribe", "fix_spelling", "soap"],
        "environment": settings.app_env,
    }
