from src.agents.mcp.client import call_clinical_tool
from src.agents.state import ClinicalState


async def transcribe_node(state: ClinicalState) -> dict:
    try:
        transcript = await call_clinical_tool(
            "transcribe_audio",
            {"audio_path": state["audio_path"]},
        )
        return {
            "transcript": transcript,
            "current_step": "transcribe",
        }
    except Exception as e:
        return {
            "error": str(e),
            "current_step": "transcribe",
        }
