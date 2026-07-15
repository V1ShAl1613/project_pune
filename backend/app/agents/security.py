"""Security helpers for agent authentication, authorization, and validation."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass(slots=True)
class SecurityDecision:
    """Security evaluation result for an execution request."""

    allowed: bool
    reason: str | None = None
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass(slots=True)
class AgentSecurityPolicy:
    """Generic policy bundle covering auth, authz, and limits."""

    required_scopes: list[str] = field(default_factory=list)
    allowed_roles: list[str] = field(default_factory=list)
    max_payload_size: int = 1024 * 1024
    max_parallel_tasks: int = 32
    rate_limit_per_minute: int = 120


class SecurityEngine:
    """Validates execution requests against a policy bundle."""

    def __init__(self, policy: AgentSecurityPolicy | None = None) -> None:
        self.policy = policy or AgentSecurityPolicy()

    def authorize(self, *, roles: list[str] | None = None, scopes: list[str] | None = None, payload_size: int = 0) -> SecurityDecision:
        if payload_size > self.policy.max_payload_size:
            return SecurityDecision(False, "payload_too_large")
        if self.policy.allowed_roles and not set(roles or []).intersection(self.policy.allowed_roles):
            return SecurityDecision(False, "insufficient_role")
        if self.policy.required_scopes and not set(scopes or []).issuperset(self.policy.required_scopes):
            return SecurityDecision(False, "insufficient_scope")
        return SecurityDecision(True)
