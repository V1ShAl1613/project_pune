from __future__ import annotations

from dataclasses import dataclass
from uuid import UUID

from app.auth.models import AuthContext
from app.auth.tokens.service import JwtService
from app.exceptions.base import AuthenticationApplicationException
from app.database.models.identity import RefreshToken, Session, User


@dataclass(slots=True)
class TokenValidator:
    jwt_service: JwtService

    def validate_access_token(self, token: str) -> AuthContext:
        payload = self.jwt_service.decode(token)
        if payload.get("type") != "access":
            raise AuthenticationApplicationException("Invalid token type")
        return self._to_auth_context(payload)

    def validate_refresh_token(self, token: str) -> AuthContext:
        payload = self.jwt_service.decode(token)
        if payload.get("type") != "refresh":
            raise AuthenticationApplicationException("Invalid token type")
        return self._to_auth_context(payload, refresh_token_jti=payload.get("jti"))

    def validate_one_time_token(self, token: str, expected_type: str) -> dict[str, object]:
        payload = self.jwt_service.decode(token)
        if payload.get("type") != expected_type:
            raise AuthenticationApplicationException("Invalid token type")
        return payload

    def _to_auth_context(self, payload: dict[str, object], refresh_token_jti: str | None = None) -> AuthContext:
        return AuthContext(
            user_id=UUID(str(payload["sub"])),
            session_id=UUID(str(payload["sid"])),
            access_token_jti=str(payload["jti"]),
            refresh_token_jti=refresh_token_jti,
            token_type=str(payload["type"]),
        )
