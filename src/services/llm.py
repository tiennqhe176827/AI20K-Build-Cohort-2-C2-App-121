from langchain_core.language_models import BaseChatModel

from src.config import get_settings


def get_llm() -> BaseChatModel:
    settings = get_settings()

    if settings.llm_provider == "gemini":
        from langchain_google_genai import ChatGoogleGenerativeAI

        return ChatGoogleGenerativeAI(
            model=settings.gemini_model_name,
            google_api_key=settings.google_api_key,
            temperature=settings.llm_temperature,
        )

    from langchain_openai import ChatOpenAI

    return ChatOpenAI(
        model=settings.model_name,
        api_key=settings.openai_api_key,
        temperature=settings.llm_temperature,
    )
