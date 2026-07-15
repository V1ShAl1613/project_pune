from __future__ import annotations

import logging
import time

from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.requests import Request
from starlette.responses import Response

from app.logging.context import get_correlation_id


class RequestLoggingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:
        started = getattr(request.state, "request_started_at", time.perf_counter())
        response = await call_next(request)
        duration_ms = (time.perf_counter() - started) * 1000.0
        logging.getLogger("sentinel.request").info(
            "request_complete",
            extra={
                "method": request.method,
                "path": request.url.path,
                "status_code": response.status_code,
                "duration_ms": round(duration_ms, 2),
                "correlation_id": get_correlation_id(),
            },
        )
        return response
