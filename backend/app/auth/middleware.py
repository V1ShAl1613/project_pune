from __future__ import annotations

from dataclasses import dataclass

from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.requests import Request
from starlette.responses import Response

from app.auth.models import AuthContext
from app.auth.tokens.service import JwtService
from app.auth.tokens.validator import TokenValidator
from app.core.settings import AppSettings


def extract_bearer_token(request: Request) -> str | None:
    authorization = request.headers.get("Authorization")
    if authorization and authorization.lower().startswith("bearer "):
        return authorization.split(" ", 1)[1].strip()
    cookie_token = request.cookies.get("access_token")
    return cookie_token


class AuthenticationMiddleware(BaseHTTPMiddleware):
    def __init__(self, app, settings: AppSettings) -> None:
        super().__init__(app)
        self.token_validator = TokenValidator(JwtService(settings))

    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:
        token = extract_bearer_token(request)
        if token is not None:
            try:
                request.state.auth_context = self.token_validator.validate_access_token(token)
            except Exception:
                request.state.auth_context = None
        response = await call_next(request)
        return response
