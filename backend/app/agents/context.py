"""Context carriers for agent, task, workflow, and environment data."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any
from uuid import UUID


@dataclass(slots=True)
class SharedContext:
    """Shared data visible across agents in a workflow."""

    values: dict[str, Any] = field(default_factory=dict)


@dataclass(slots=True)
class AgentContext:
    """Agent-local execution context."""

    agent_id: UUID | None = None
    task_id: UUID | None = None
    workflow_id: UUID | None = None
    user_context: dict[str, Any] = field(default_factory=dict)
    organization_context: dict[str, Any] = field(default_factory=dict)
    workspace_context: dict[str, Any] = field(default_factory=dict)
    conversation_context: dict[str, Any] = field(default_factory=dict)
    execution_context: dict[str, Any] = field(default_factory=dict)
    shared_context: SharedContext = field(default_factory=SharedContext)


@dataclass(slots=True)
class ContextEnvelope:
    """Normalized context bundle passed into runtime and workflow execution."""

    agent: AgentContext = field(default_factory=AgentContext)
    task: dict[str, Any] = field(default_factory=dict)
    workflow: dict[str, Any] = field(default_factory=dict)
    metadata: dict[str, Any] = field(default_factory=dict)
