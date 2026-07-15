"""Agent execution records used by the orchestrator and monitoring layer."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any
from uuid import UUID, uuid4


@dataclass(slots=True)
class ExecutionRecord:
    """Execution metadata for a task or workflow step."""

    execution_id: UUID = field(default_factory=uuid4)
    agent_id: UUID | None = None
    task_id: UUID | None = None
    workflow_id: UUID | None = None
    status: str = "running"
    started_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    completed_at: datetime | None = None
    input_context: dict[str, Any] = field(default_factory=dict)
    output_context: dict[str, Any] = field(default_factory=dict)
    metadata: dict[str, Any] = field(default_factory=dict)
    error_message: str | None = None
