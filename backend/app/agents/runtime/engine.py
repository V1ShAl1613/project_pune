"""Agent runtime engine and lifecycle management."""

from __future__ import annotations

import asyncio
import time
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Awaitable, Callable
from uuid import UUID

from app.agents.communication import MessageBus, MessageEnvelope
from app.agents.context import ContextEnvelope
from app.agents.core.contracts import AgentExecutionContext, AgentExecutionResult, BaseAgent
from app.agents.monitoring import AgentHealthSnapshot
from app.agents.registry.registry import AgentMetadata, AgentRegistry
from app.agents.scheduler.scheduler import AgentScheduler, ScheduledItem
from app.agents.security import SecurityEngine
from app.agents.governance import GovernanceEngine
from app.agents.validators import AgentValidator


class AgentFactory:
    """Creates agents from callables or existing instances."""

    def create(self, factory: Callable[[], BaseAgent] | BaseAgent) -> BaseAgent:
        return factory() if callable(factory) and not isinstance(factory, BaseAgent) else factory  # type: ignore[return-value]


class AgentLoader:
    """Loads agent definitions into the registry."""

    def __init__(self, registry: AgentRegistry) -> None:
        self.registry = registry

    def load(self, agent: BaseAgent, *, namespace: str = "default", configuration: dict[str, Any] | None = None, priority: int = 50, dependencies: list[str] | None = None) -> AgentMetadata:
        return self.registry.register(agent, namespace=namespace, configuration=configuration, priority=priority, dependencies=dependencies)


class AgentLifecycleManager:
    """Coordinates lifecycle transitions for registered agents."""

    def __init__(self, registry: AgentRegistry) -> None:
        self.registry = registry

    async def initialize(self, agent_id: UUID) -> None:
        agent = self.registry.get(agent_id)
        if agent is not None:
            await agent.initialize()
            self.registry.update_status(agent_id, "initialized", health=await agent.health_check())

    async def start(self, agent_id: UUID) -> None:
        agent = self.registry.get(agent_id)
        if agent is not None:
            await agent.start()
            self.registry.update_status(agent_id, "running", health=await agent.health_check())

    async def pause(self, agent_id: UUID) -> None:
        agent = self.registry.get(agent_id)
        if agent is not None:
            await agent.pause()
            self.registry.update_status(agent_id, "paused", health=await agent.health_check())

    async def resume(self, agent_id: UUID) -> None:
        agent = self.registry.get(agent_id)
        if agent is not None:
            await agent.resume()
            self.registry.update_status(agent_id, "running", health=await agent.health_check())

    async def restart(self, agent_id: UUID) -> None:
        agent = self.registry.get(agent_id)
        if agent is not None:
            await agent.restart()
            self.registry.update_status(agent_id, "running", health=await agent.health_check())

    async def shutdown(self, agent_id: UUID) -> None:
        agent = self.registry.get(agent_id)
        if agent is not None:
            await agent.shutdown()
            self.registry.update_status(agent_id, "stopped", health=await agent.health_check())

    async def unload(self, agent_id: UUID) -> None:
        agent = self.registry.get(agent_id)
        if agent is not None:
            await agent.unload()
            self.registry.update_status(agent_id, "unloaded", health=await agent.health_check())

    async def destroy(self, agent_id: UUID) -> None:
        agent = self.registry.get(agent_id)
        if agent is not None:
            await agent.destroy()
            self.registry.update_status(agent_id, "destroyed", health=await agent.health_check())


class AgentExecutor:
    """Executes agent work with retry and timeout handling."""

    async def execute(self, agent: BaseAgent, context: AgentExecutionContext, *, timeout_seconds: float = 300.0, retry_attempts: int = 3) -> AgentExecutionResult:
        last_error: str | None = None
        for attempt in range(retry_attempts + 1):
            try:
                return await asyncio.wait_for(agent.execute(context), timeout=timeout_seconds)
            except Exception as exc:  # pragma: no cover - runtime safety net
                last_error = str(exc)
                if attempt >= retry_attempts:
                    break
                await asyncio.sleep(min(0.5 * (attempt + 1), 2.0))
        return AgentExecutionResult(success=False, error=last_error)


class AgentCoordinator:
    """Routes work to the best available agent."""

    def __init__(self, registry: AgentRegistry) -> None:
        self.registry = registry

    def choose(self, *, agent_id: UUID | None = None, agent_type: str | None = None, capability: str | None = None, namespace: str | None = None) -> BaseAgent | None:
        if agent_id is not None:
            return self.registry.get(agent_id)
        candidates = self.registry.discover(agent_type=agent_type, capability=capability, namespace=namespace)
        if not candidates:
            return None
        chosen = candidates[0]
        return self.registry.get(chosen.agent_id)


class AgentSupervisor:
    """Produces platform-wide health and telemetry snapshots."""

    def __init__(self, registry: AgentRegistry, scheduler: AgentScheduler, message_bus: MessageBus | None = None) -> None:
        self.registry = registry
        self.scheduler = scheduler
        self.message_bus = message_bus or MessageBus()

    def snapshot(self) -> AgentHealthSnapshot:
        metadata = self.registry.list()
        running = sum(1 for item in metadata if item.status == "running")
        failures = sum(1 for item in metadata if item.status == "error")
        return AgentHealthSnapshot(
            active_agents=len(metadata),
            running_tasks=self.scheduler.size(),
            completed_tasks=0,
            workflow_count=0,
            execution_time_ms=0.0,
            failures=failures,
            retries=0,
            queue_size=self.scheduler.size(),
            health_status="healthy" if failures == 0 else "degraded",
        )


@dataclass(slots=True)
class AgentManager:
    """Facade wiring registry, lifecycle, executor, scheduler, and governance together."""

    registry: AgentRegistry = field(default_factory=AgentRegistry)
    scheduler: AgentScheduler = field(default_factory=AgentScheduler)
    message_bus: MessageBus = field(default_factory=MessageBus)
    security_engine: SecurityEngine = field(default_factory=SecurityEngine)
    governance_engine: GovernanceEngine = field(default_factory=GovernanceEngine)
    validator: AgentValidator = field(default_factory=AgentValidator)
    factory: AgentFactory = field(init=False)
    loader: AgentLoader = field(init=False)
    lifecycle: AgentLifecycleManager = field(init=False)
    executor: AgentExecutor = field(init=False)
    coordinator: AgentCoordinator = field(init=False)
    supervisor: AgentSupervisor = field(init=False)

    def __post_init__(self) -> None:
        self.factory = AgentFactory()
        self.loader = AgentLoader(self.registry)
        self.lifecycle = AgentLifecycleManager(self.registry)
        self.executor = AgentExecutor()
        self.coordinator = AgentCoordinator(self.registry)
        self.supervisor = AgentSupervisor(self.registry, self.scheduler, self.message_bus)

    def register(self, agent: BaseAgent, *, namespace: str = "default", configuration: dict[str, Any] | None = None, priority: int = 50, dependencies: list[str] | None = None) -> AgentMetadata:
        return self.loader.load(agent, namespace=namespace, configuration=configuration, priority=priority, dependencies=dependencies)

    async def enqueue(self, *, priority: int, payload: dict[str, Any]) -> UUID:
        return await self.scheduler.schedule(priority=priority, payload=payload)

    async def publish(self, topic: str, payload: dict[str, Any], *, sender: str | None = None, recipient: str | None = None) -> None:
        await self.message_bus.publish(MessageEnvelope(topic=topic, payload=payload, sender=sender, recipient=recipient))

    def health(self) -> AgentHealthSnapshot:
        return self.supervisor.snapshot()
