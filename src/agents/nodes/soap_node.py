from src.agents.mcp.client import call_clinical_tool
from src.agents.state import ClinicalState


async def soap_node(state: ClinicalState) -> dict:
    try:
        soap_note = await call_clinical_tool(
            "convert_to_soap_note",
            {"transcript": state["corrected_transcript"]},
        )
        return {
            "soap_note": soap_note,
            "current_step": "soap",
        }
    except Exception as e:
        return {
            "error": str(e),
            "current_step": "soap",
        }
