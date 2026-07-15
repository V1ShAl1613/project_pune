"""Task helper models for orchestration and execution."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any
from uuid import UUID, uuid4


@dataclass(slots=True)
class TaskEnvelope:
    """Queued task envelope used by the orchestrator."""

    task_id: UUID = field(default_factory=uuid4)
    agent_id: UUID | None = None
    workflow_id: UUID | None = None
    title: str = ""
    task_type: str = "general"
    priority: int = 50
    payload: dict[str, Any] = field(default_factory=dict)
    context: dict[str, Any] = field(default_factory=dict)
    metadata: dict[str, Any] = field(default_factory=dict)
