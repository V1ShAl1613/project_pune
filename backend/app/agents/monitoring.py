"""Monitoring models for runtime health and execution metrics."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any


@dataclass(slots=True)
class AgentHealthSnapshot:
    """Current health snapshot for the agent platform."""

    active_agents: int = 0
    running_tasks: int = 0
    completed_tasks: int = 0
    workflow_count: int = 0
    execution_time_ms: float = 0.0
    failures: int = 0
    retries: int = 0
    queue_size: int = 0
    health_status: str = "healthy"
    updated_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    metadata: dict[str, Any] = field(default_factory=dict)
