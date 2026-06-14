from src.agents.mcp.client import call_clinical_tool
from src.agents.state import ClinicalState


async def fix_spelling_node(state: ClinicalState) -> dict:
    try:
        corrected = await call_clinical_tool(
            "fix_spelling",
            {"text": state["transcript"]},
        )
        return {
            "corrected_transcript": corrected,
            "current_step": "fix_spelling",
        }
    except Exception as e:
        return {
            "error": str(e),
            "current_step": "fix_spelling",
        }
