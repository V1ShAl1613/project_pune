from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from uuid import UUID


@dataclass(slots=True)
class AuthContext:
    user_id: UUID
    session_id: UUID
    access_token_jti: str
    refresh_token_jti: str | None
    token_type: str
    device_id: str | None = None
    device_name: str | None = None
    ip_address: str | None = None
    user_agent: str | None = None
    authenticated_at: datetime | None = None


@dataclass(slots=True)
class TokenPair:
    access_token: str
    refresh_token: str
    access_expires_in: int
    refresh_expires_in: int
    access_jti: str
    refresh_jti: str
    family_id: str


@dataclass(slots=True)
class AuthRequestContext:
    ip_address: str | None = None
    user_agent: str | None = None
    device_id: str | None = None
    device_name: str | None = None
    device_fingerprint: str | None = None
    geo_location: dict[str, object] | None = None
