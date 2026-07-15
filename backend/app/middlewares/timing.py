from __future__ import annotations

import time

from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.requests import Request
from starlette.responses import Response

from app.metrics.collector import metrics_collector


class RequestTimingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:
        started = time.perf_counter()
        request.state.request_started_at = started
        response = await call_next(request)
        duration_ms = (time.perf_counter() - started) * 1000.0
        response.headers["X-Process-Time-MS"] = f"{duration_ms:.2f}"
        metrics_collector.record_request(request.method, request.url.path, response.status_code, duration_ms)
        return response
