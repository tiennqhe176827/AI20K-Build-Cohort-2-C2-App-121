from __future__ import annotations
from typing import Any
from langchain_mcp_adapters.client import MultiServerMCPClient
from src.config import get_settings

settings = get_settings()

mcp_client = MultiServerMCPClient(
    {
        "clinical": {
            "url": settings.mcp_clinical_url,
            "transport": "streamable_http",
        }
    }
)


def _extract_tool_text(result: Any) -> str:
    if isinstance(result, str):
        return result.strip()

    content = getattr(result, "content", None)
    if content:
        parts: list[str] = []
        for block in content:
            text = getattr(block, "text", None)
            if text:
                parts.append(text)
        if parts:
            return "".join(parts).strip()

    if isinstance(result, dict):
        if "text" in result:
            return str(result["text"]).strip()
        if "content" in result and isinstance(result["content"], list):
            parts = []
            for block in result["content"]:
                if isinstance(block, dict) and block.get("text"):
                    parts.append(block["text"])
            if parts:
                return "".join(parts).strip()

    return str(result).strip()


async def call_clinical_tool(tool_name: str, arguments: dict[str, Any]) -> str:
    try:
        async with mcp_client.session("clinical") as session:
            result = await session.call_tool(tool_name, arguments)
        return _extract_tool_text(result)
    except BaseExceptionGroup as eg:
        msg = str(eg.exceptions[0]) if eg.exceptions else str(eg)
        raise RuntimeError(
            f"Lỗi kết nối MCP server ({settings.mcp_clinical_url}): {msg}"
        ) from eg
