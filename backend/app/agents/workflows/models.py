"""Workflow definition helpers for orchestration execution."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any
from uuid import UUID, uuid4


@dataclass(slots=True)
class WorkflowStepDefinition:
    """Serializable workflow step definition."""

    name: str
    agent_type: str | None = None
    task_type: str = "general"
    condition: str | None = None
    retry_attempts: int = 3
    timeout_seconds: float = 300.0
    parallel: bool = False
    payload: dict[str, Any] = field(default_factory=dict)


@dataclass(slots=True)
class WorkflowDefinition:
    """Serializable workflow definition used by the orchestrator."""

    id: UUID = field(default_factory=uuid4)
    name: str = ""
    version: str = "1.0.0"
    description: str | None = None
    steps: list[WorkflowStepDefinition] = field(default_factory=list)
    policy: dict[str, Any] = field(default_factory=dict)
