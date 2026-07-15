from __future__ import annotations

from uuid import uuid4

from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.requests import Request
from starlette.responses import Response

from app.logging.context import set_correlation_id, set_request_path


class CorrelationIdMiddleware(BaseHTTPMiddleware):
    def __init__(self, app, header_name: str) -> None:
        super().__init__(app)
        self.header_name = header_name

    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:
        correlation_id = request.headers.get(self.header_name, str(uuid4()))
        request.state.correlation_id = correlation_id
        set_correlation_id(correlation_id)
        set_request_path(request.url.path)
        response = await call_next(request)
        response.headers[self.header_name] = correlation_id
        return response
