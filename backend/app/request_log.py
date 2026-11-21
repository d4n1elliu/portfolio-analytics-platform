"""Logs one line for each request: its method, path, status and how long it took."""

import logging
import time

from fastapi import Request, status

logger = logging.getLogger("app.requests")

LOG_FORMAT = "%(asctime)s %(levelname)s %(name)s %(message)s"
UNLOGGED_PATHS = frozenset({"/health"})


def describe_request(method: str, path: str, status_code: int, seconds: float) -> str:
    return f"{method} {path} {status_code} {seconds * 1000:.0f}ms"


async def log_request(request: Request, call_next):
    started = time.perf_counter()
    status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
    try:
        response = await call_next(request)
        status_code = response.status_code
        return response
    finally:
        path = request.url.path
        if path not in UNLOGGED_PATHS:
            seconds = time.perf_counter() - started
            logger.info(describe_request(request.method, path, status_code, seconds))
