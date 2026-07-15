from __future__ import annotations

from uuid import UUID

from app.agents.core.contracts import AgentExecutionContext, AgentExecutionResult, BaseAgent
from app.agents.runtime.engine import AgentManager
from app.agents.schemas import AgentCreateRequest, WorkflowCreateRequest, WorkflowStep
from app.agents.services.agent_service import AgentService


class DummyAgent(BaseAgent):
    async def execute(self, context: AgentExecutionContext) -> AgentExecutionResult:
        return AgentExecutionResult(success=True, output={"ok": True, "agent": self.name, "task": str(context.task_id) if context.task_id else None})


def test_agent_registry_and_health_snapshot() -> None:
    manager = AgentManager()
    agent = DummyAgent(name="worker-1", agent_type="worker")

    metadata = manager.register(agent, priority=10)

    assert metadata.name == "worker-1"
    snapshot = manager.health()
    assert snapshot.active_agents == 1
    assert snapshot.health_status == "healthy"


def test_agent_service_creates_workflow_and_agent() -> None:
    service = AgentService(repository=None)

    agent_response = __import__("asyncio").run(service.create_agent(AgentCreateRequest(name="planner-1", agent_type="planner")))
    workflow_response = __import__("asyncio").run(
        service.create_workflow(
            WorkflowCreateRequest(
                name="coordination-flow",
                steps=[WorkflowStep(name="step-1", agent_type="planner")],
            )
        )
    )

    assert agent_response.name == "planner-1"
    assert workflow_response.name == "coordination-flow"
