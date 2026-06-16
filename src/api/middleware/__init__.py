from src.api.middleware.cors import setup_cors
from src.api.middleware.error_handler import setup_error_handlers
from src.api.middleware.logging import setup_logging_middleware
from src.api.middleware.rate_limit import setup_rate_limit

__all__ = ["setup_cors", "setup_error_handlers", "setup_logging_middleware", "setup_rate_limit"]


def setup_all_middleware(app) -> None:
    setup_error_handlers(app)
    setup_cors(app)
    setup_logging_middleware(app)
    setup_rate_limit(app)
