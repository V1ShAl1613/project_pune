from __future__ import annotations

import time
from collections import defaultdict, deque

from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.requests import Request
from starlette.responses import Response

from app.core.settings import AppSettings


class RateLimitMiddleware(BaseHTTPMiddleware):
    def __init__(self, app, settings: AppSettings, limit: int = 100, window_seconds: int = 60) -> None:
        super().__init__(app)
        self.settings = settings
        self.limit = limit
        self.window_seconds = window_seconds
        self._requests: dict[str, deque[float]] = defaultdict(deque)

    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:
        if not self.settings.enable_rate_limit:
            return await call_next(request)

        client_key = request.client.host if request.client else "anonymous"
        request_times = self._requests[client_key]
        now = time.time()
        while request_times and now - request_times[0] > self.window_seconds:
            request_times.popleft()
        if len(request_times) >= self.limit:
            return Response(content='{"detail":"rate limit exceeded"}', status_code=429, media_type="application/json")
        request_times.append(now)
        return await call_next(request)
