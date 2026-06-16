import time

from fastapi import FastAPI, Request
from starlette.middleware.base import BaseHTTPMiddleware

from src.core.logging import get_logger

logger = get_logger("middleware.access")


class AccessLogMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        start = time.perf_counter()
        response = await call_next(request)
        elapsed_ms = (time.perf_counter() - start) * 1000

        logger.info(
            "%s %s -> %s (%.1fms)",
            request.method,
            request.url.path,
            response.status_code,
            elapsed_ms,
        )
        return response


def setup_logging_middleware(app: FastAPI) -> None:
    app.add_middleware(AccessLogMiddleware)
