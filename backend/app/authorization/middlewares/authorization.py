from __future__ import annotations

from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.requests import Request
from starlette.responses import Response

from app.authorization.dependencies import build_authorization_service
from app.authorization.repositories.cache_repository import AuthorizationCacheRepository
from app.core.settings import AppSettings


class AuthorizationMiddleware(BaseHTTPMiddleware):
    def __init__(self, app, settings: AppSettings) -> None:
        super().__init__(app)
        self.settings = settings

    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:
        auth_context = getattr(request.state, "auth_context", None)
        redis_client = getattr(request.app.state, "redis_client", None)
        if auth_context is not None and redis_client is not None:
            cache = AuthorizationCacheRepository(redis_client)
            request.state.authorization_context = await cache.get_context(auth_context.user_id)
        response = await call_next(request)
        return response

