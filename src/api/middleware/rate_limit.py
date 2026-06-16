import time
from collections import defaultdict

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware


class RateLimitMiddleware(BaseHTTPMiddleware):
    def __init__(self, app, max_requests: int = 60, window_seconds: int = 60):
        super().__init__(app)
        self.max_requests = max_requests
        self.window_seconds = window_seconds
        self._requests: dict[str, list[float]] = defaultdict(list)

    def _get_client_id(self, request: Request) -> str:
        forwarded = request.headers.get("X-Forwarded-For")
        if forwarded:
            return forwarded.split(",")[0].strip()
        return request.client.host if request.client else "unknown"

    async def dispatch(self, request: Request, call_next):
        client_id = self._get_client_id(request)
        now = time.time()
        cutoff = now - self.window_seconds

        self._requests[client_id] = [t for t in self._requests[client_id] if t > cutoff]

        if len(self._requests[client_id]) >= self.max_requests:
            return JSONResponse(
                status_code=429,
                content={"detail": "Quá nhiều requests. Vui lòng thử lại sau."},
            )

        self._requests[client_id].append(now)
        return await call_next(request)


def setup_rate_limit(app: FastAPI) -> None:
    app.add_middleware(RateLimitMiddleware, max_requests=60, window_seconds=60)
