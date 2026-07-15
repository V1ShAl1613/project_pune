from __future__ import annotations

import base64
import hashlib
import hmac
import json
import secrets
from dataclasses import dataclass
from datetime import UTC, datetime, timedelta
from typing import Any

try:  # pragma: no cover - optional dependency
    import jwt as pyjwt
except ModuleNotFoundError:  # pragma: no cover
    pyjwt = None

try:  # pragma: no cover - optional dependency
    from jose import jwt as jose_jwt
except ModuleNotFoundError:  # pragma: no cover
    jose_jwt = None

from app.core.settings import AppSettings
from app.exceptions.base import AuthenticationApplicationException


def _json_default(value: Any) -> str:
    if isinstance(value, datetime):
        return value.astimezone(UTC).isoformat()
    raise TypeError(f"Unsupported value: {type(value)!r}")


def _base64_url_encode(value: bytes) -> str:
    return base64.urlsafe_b64encode(value).rstrip(b"=").decode("ascii")


def _base64_url_decode(value: str) -> bytes:
    padding = "=" * (-len(value) % 4)
    return base64.urlsafe_b64decode(value + padding)


@dataclass(slots=True)
class JwtService:
    settings: AppSettings

    def encode(self, payload: dict[str, Any]) -> str:
        if pyjwt is not None:
            return pyjwt.encode(payload, self.settings.jwt_secret_key, algorithm=self.settings.jwt_algorithm)
        if jose_jwt is not None:
            return jose_jwt.encode(payload, self.settings.jwt_secret_key, algorithm=self.settings.jwt_algorithm)
        return self._encode_fallback(payload)

    def decode(self, token: str) -> dict[str, Any]:
        try:
            if pyjwt is not None:
                return pyjwt.decode(
                    token,
                    self.settings.jwt_secret_key,
                    algorithms=[self.settings.jwt_algorithm],
                    audience=self.settings.jwt_audience,
                    issuer=self.settings.jwt_issuer,
                    options={"require": ["exp", "iat", "jti", "sub", "type"]},
                )
            if jose_jwt is not None:
                return jose_jwt.decode(
                    token,
                    self.settings.jwt_secret_key,
                    algorithms=[self.settings.jwt_algorithm],
                    audience=self.settings.jwt_audience,
                    issuer=self.settings.jwt_issuer,
                    options={"require_exp": True, "require_iat": True, "require_sub": True},
                )
            return self._decode_fallback(token)
        except Exception as exc:  # pragma: no cover - defensive translation
            raise AuthenticationApplicationException(str(exc)) from exc

    def hash_token(self, token: str) -> str:
        digest = hashlib.sha256(token.encode("utf-8")).hexdigest()
        return digest

    def create_claims(
        self,
        *,
        subject: str,
        token_type: str,
        expires_in: int,
        jti: str | None = None,
        extra_claims: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        issued_at = datetime.now(UTC)
        expires_at = issued_at + timedelta(seconds=expires_in)
        claims: dict[str, Any] = {
            "sub": subject,
            "type": token_type,
            "iss": self.settings.jwt_issuer,
            "aud": self.settings.jwt_audience,
            "iat": int(issued_at.timestamp()),
            "nbf": int(issued_at.timestamp()),
            "exp": int(expires_at.timestamp()),
            "jti": jti or secrets.token_urlsafe(16),
        }
        if extra_claims:
            claims.update(extra_claims)
        return claims

    def _encode_fallback(self, payload: dict[str, Any]) -> str:
        header = {"alg": "HS256", "typ": "JWT"}
        header_segment = _base64_url_encode(json.dumps(header).encode("utf-8"))
        payload_segment = _base64_url_encode(json.dumps(payload, default=_json_default).encode("utf-8"))
        signing_input = f"{header_segment}.{payload_segment}".encode("ascii")
        signature = hmac.new(
            self.settings.jwt_secret_key.encode("utf-8"),
            signing_input,
            hashlib.sha256,
        ).digest()
        return f"{header_segment}.{payload_segment}.{_base64_url_encode(signature)}"

    def _decode_fallback(self, token: str) -> dict[str, Any]:
        header_segment, payload_segment, signature_segment = token.split(".")
        signing_input = f"{header_segment}.{payload_segment}".encode("ascii")
        expected_signature = hmac.new(
            self.settings.jwt_secret_key.encode("utf-8"),
            signing_input,
            hashlib.sha256,
        ).digest()
        provided_signature = _base64_url_decode(signature_segment)
        if not hmac.compare_digest(expected_signature, provided_signature):
            raise AuthenticationApplicationException("Invalid token signature")
        payload = json.loads(_base64_url_decode(payload_segment))
        now = int(datetime.now(UTC).timestamp())
        if payload.get("exp") and now >= int(payload["exp"]):
            raise AuthenticationApplicationException("Token expired")
        if payload.get("iss") != self.settings.jwt_issuer:
            raise AuthenticationApplicationException("Invalid issuer")
        if payload.get("aud") != self.settings.jwt_audience:
            raise AuthenticationApplicationException("Invalid audience")
        return payload
