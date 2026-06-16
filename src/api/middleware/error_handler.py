from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from src.core.exceptions import AppError
from src.core.logging import get_logger

logger = get_logger("middleware.error")


async def app_error_handler(request: Request, exc: AppError) -> JSONResponse:
    logger.warning("AppError: %s %s -> %d %s", request.method, request.url.path, exc.status_code, exc.detail)
    return JSONResponse(status_code=exc.status_code, content={"detail": exc.detail})


async def unhandled_error_handler(request: Request, exc: Exception) -> JSONResponse:
    logger.exception("Unhandled error: %s %s", request.method, request.url.path)
    return JSONResponse(status_code=500, content={"detail": "Internal server error"})


def setup_error_handlers(app: FastAPI) -> None:
    app.add_exception_handler(AppError, app_error_handler)
    app.add_exception_handler(Exception, unhandled_error_handler)
