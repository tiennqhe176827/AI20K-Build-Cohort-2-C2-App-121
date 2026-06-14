from google import genai

from src.config import get_settings

settings = get_settings()

_api_key = settings.google_api_key or settings.gemini_api_key

client = genai.Client(api_key=_api_key)
