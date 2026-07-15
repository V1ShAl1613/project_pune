"""Governance primitives for approvals, retention, and usage policies."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import timedelta
from typing import Any


@dataclass(slots=True)
class GovernanceDecision:
    """Outcome of a policy evaluation."""

    allowed: bool
    approval_required: bool = False
    reason: str | None = None
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass(slots=True)
class GovernancePolicy:
    """Generic governance policy for the runtime."""

    approval_required: bool = False
    retention_days: int = 365
    max_task_retries: int = 3
    max_parallel_tasks: int = 32
    usage_notes: str | None = None

    @property
    def retention(self) -> timedelta:
        return timedelta(days=self.retention_days)


class GovernanceEngine:
    """Evaluates execution requests against governance rules."""

    def __init__(self, policy: GovernancePolicy | None = None) -> None:
        self.policy = policy or GovernancePolicy()

    def evaluate(self, *, task_type: str, priority: int, requires_approval: bool = False) -> GovernanceDecision:
        if requires_approval or self.policy.approval_required:
            return GovernanceDecision(True, approval_required=True, reason="approval_required", metadata={"task_type": task_type, "priority": priority})
        return GovernanceDecision(True, metadata={"task_type": task_type, "priority": priority})
