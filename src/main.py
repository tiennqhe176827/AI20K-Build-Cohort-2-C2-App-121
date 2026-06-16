from contextlib import asynccontextmanager

from fastapi import FastAPI

from src.api import router
from src.api.middleware import setup_all_middleware
from src.config import get_settings
from src.core.logging import setup_logging
from src.database.engine import init_db


@asynccontextmanager
async def lifespan(app: FastAPI):
    settings = get_settings()
    setup_logging()
    init_db()
    print(f"Starting {settings.app_name} in {settings.app_env} mode")
    yield
    print("Shutting down...")


def create_app() -> FastAPI:
    settings = get_settings()

    app = FastAPI(
        title="AI20K Agent",
        description="AI Agent built with LangGraph for clinical SOAP notes",
        version="1.0.0",
        lifespan=lifespan,
    )

    setup_all_middleware(app)
    app.include_router(router)

    @app.get("/health")
    async def health():
        return {"status": "ok", "env": settings.app_env}

    return app


app = create_app()
