from __future__ import annotations

from dataclasses import dataclass, field
from uuid import UUID


@dataclass(slots=True)
class AuthorizationContext:
    user_id: UUID
    session_id: UUID
    role_codes: set[str] = field(default_factory=set)
    permission_codes: set[str] = field(default_factory=set)
    policy_codes: set[str] = field(default_factory=set)
    is_super_admin: bool = False


@dataclass(slots=True)
class AuthorizationDecision:
    allowed: bool
    reason: str
    matched_policy: str | None = None
    matched_permission: str | None = None

