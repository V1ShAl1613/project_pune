from __future__ import annotations

import secrets
from dataclasses import dataclass


@dataclass(slots=True)
class CsrfProtection:
    """CSRF protection skeleton for cookie-based authentication flows."""

    header_name: str = "X-CSRF-Token"
    cookie_name: str = "csrf_token"

    def generate_token(self) -> str:
        return secrets.token_urlsafe(32)

    def validate_token(self, expected: str | None, provided: str | None) -> bool:
        return bool(expected and provided and secrets.compare_digest(expected, provided))
