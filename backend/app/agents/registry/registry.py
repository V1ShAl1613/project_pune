"""In-memory agent registry with metadata and health tracking."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any
from uuid import UUID

from app.agents.core.contracts import BaseAgent


@dataclass(slots=True)
class AgentMetadata:
    """Registry metadata for an agent definition."""

    agent_id: UUID
    name: str
    namespace: str
    version: str
    agent_type: str
    capabilities: list[str] = field(default_factory=list)
    dependencies: list[str] = field(default_factory=list)
    configuration: dict[str, Any] = field(default_factory=dict)
    status: str = "registered"
    priority: int = 50
    health: dict[str, Any] = field(default_factory=dict)
    registered_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


class AgentRegistry:
    """Registry for discovering and managing agents."""

    def __init__(self) -> None:
        self._agents: dict[UUID, BaseAgent] = {}
        self._metadata: dict[UUID, AgentMetadata] = {}

    def register(self, agent: BaseAgent, *, namespace: str = "default", configuration: dict[str, Any] | None = None, priority: int = 50, dependencies: list[str] | None = None) -> AgentMetadata:
        metadata = AgentMetadata(
            agent_id=agent.id,
            name=agent.name,
            namespace=namespace,
            version=agent.version,
            agent_type=agent.agent_type,
            capabilities=list(agent.capabilities),
            dependencies=dependencies or [],
            configuration=configuration or {},
            status="registered",
            priority=priority,
        )
        self._agents[agent.id] = agent
        self._metadata[agent.id] = metadata
        return metadata

    def unregister(self, agent_id: UUID) -> None:
        self._agents.pop(agent_id, None)
        self._metadata.pop(agent_id, None)

    def list(self) -> list[AgentMetadata]:
        return sorted(self._metadata.values(), key=lambda item: (-item.priority, item.name))

    def get(self, agent_id: UUID) -> BaseAgent | None:
        return self._agents.get(agent_id)

    def get_metadata(self, agent_id: UUID) -> AgentMetadata | None:
        return self._metadata.get(agent_id)

    def discover(self, *, agent_type: str | None = None, capability: str | None = None, namespace: str | None = None) -> list[AgentMetadata]:
        results = self.list()
        if agent_type is not None:
            results = [item for item in results if item.agent_type == agent_type]
        if capability is not None:
            results = [item for item in results if capability in item.capabilities]
        if namespace is not None:
            results = [item for item in results if item.namespace == namespace]
        return results

    def update_status(self, agent_id: UUID, status: str, *, health: dict[str, Any] | None = None) -> None:
        metadata = self._metadata.get(agent_id)
        if metadata is not None:
            metadata.status = status
            if health is not None:
                metadata.health = health

    def health(self, agent_id: UUID) -> dict[str, Any]:
        metadata = self._metadata.get(agent_id)
        if metadata is None:
            return {"status": "unknown"}
        return {"status": metadata.status, **metadata.health}
