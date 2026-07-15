"""Base agent contracts used by the runtime and orchestrator."""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import StrEnum
from typing import Any
from uuid import UUID, uuid4


class AgentLifecycleState(StrEnum):
    INITIALIZED = "initialized"
    STARTED = "started"
    PAUSED = "paused"
    STOPPED = "stopped"
    UNLOADED = "unloaded"
    DESTROYED = "destroyed"


@dataclass(slots=True)
class AgentExecutionContext:
    """Execution context passed into agents."""

    agent_id: UUID | None = None
    task_id: UUID | None = None
    workflow_id: UUID | None = None
    conversation_id: UUID | None = None
    user_context: dict[str, Any] = field(default_factory=dict)
    organization_context: dict[str, Any] = field(default_factory=dict)
    workspace_context: dict[str, Any] = field(default_factory=dict)
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass(slots=True)
class AgentExecutionResult:
    """Normalized agent execution result."""

    success: bool
    output: dict[str, Any] = field(default_factory=dict)
    metadata: dict[str, Any] = field(default_factory=dict)
    error: str | None = None
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


class BaseAgent(ABC):
    """Base contract for all generic enterprise agents."""

    def __init__(self, *, name: str, agent_type: str, version: str = "1.0.0", capabilities: list[str] | None = None) -> None:
        self.id = uuid4()
        self.name = name
        self.agent_type = agent_type
        self.version = version
        self.capabilities = capabilities or []
        self.state = AgentLifecycleState.INITIALIZED

    async def initialize(self) -> None:
        self.state = AgentLifecycleState.INITIALIZED

    async def load(self) -> None:
        self.state = AgentLifecycleState.INITIALIZED

    async def start(self) -> None:
        self.state = AgentLifecycleState.STARTED

    async def pause(self) -> None:
        self.state = AgentLifecycleState.PAUSED

    async def resume(self) -> None:
        self.state = AgentLifecycleState.STARTED

    async def restart(self) -> None:
        await self.shutdown()
        await self.start()

    async def shutdown(self) -> None:
        self.state = AgentLifecycleState.STOPPED

    async def unload(self) -> None:
        self.state = AgentLifecycleState.UNLOADED

    async def destroy(self) -> None:
        self.state = AgentLifecycleState.DESTROYED

    async def health_check(self) -> dict[str, Any]:
        return {"status": "healthy", "state": self.state.value}

    @abstractmethod
    async def execute(self, context: AgentExecutionContext) -> AgentExecutionResult:
        raise NotImplementedError
