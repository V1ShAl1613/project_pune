from __future__ import annotations

import logging

from app.core.settings import TestingSettings
from app.reasoning.dependencies import provide_reasoning_service
from app.reasoning.repositories.reasoning_repository import ReasoningRepository
from app.reasoning.schemas import EvaluationSampleRequest, ReasoningEvaluateRequest, ReasoningRequest, ReasoningStrategy, RiskAnalyzeRequest
from app.reasoning.services.reasoning_service import ReasoningService


class _FakeReasoningService:
    def __init__(self) -> None:
        self.service = ReasoningService(repository=ReasoningRepository(), settings=TestingSettings(), redis_client=None, logger=logging.getLogger("test"))

    async def analyze(self, payload):
        return await self.service.analyze(payload)

    async def validate(self, payload):
        return await self.service.validate(payload)

    async def explain(self, payload):
        return await self.service.explain(payload)

    async def evaluate(self, payload):
        return await self.service.evaluate(payload)

    async def risk_analyze(self, payload):
        return await self.service.risk_analyze(payload)

    async def risk_project(self, payload):
        return await self.service.risk_project(payload)

    async def recommendations(self):
        return []

    async def confidence(self):
        return []

    async def trust(self):
        return []

    async def evaluations(self):
        return []

    async def metrics(self):
        return await self.service.metrics()


def test_reasoning_analyze_route_is_registered(client, app) -> None:
    app.dependency_overrides[provide_reasoning_service] = lambda: _FakeReasoningService()
    try:
        response = client.post(
            "/reasoning/analyze",
            json={
                "query": "Assess vendor exposure",
                "strategy": ReasoningStrategy.HYBRID.value,
                "knowledge_sources": ["policy"],
                "source_references": ["https://example.invalid/ref"],
                "evidence": [{"source_type": "knowledge", "source_name": "policy", "claim": "Vendor exposure is limited", "reference_uri": "https://example.invalid/ref", "score": 88, "verified": True}],
            },
        )
    finally:
        app.dependency_overrides.clear()

    assert response.status_code == 200
    payload = response.json()
    assert payload["query"] == "Assess vendor exposure"
    assert payload["confidence"]["overall_confidence"] >= 0


def test_reasoning_evaluate_returns_scorecard() -> None:
    service = ReasoningService(repository=ReasoningRepository(), settings=TestingSettings(), redis_client=None, logger=logging.getLogger("test"))
    evaluation = __import__("asyncio").run(
        service.evaluate(
            ReasoningEvaluateRequest(
                dataset_name="golden",
                samples=[EvaluationSampleRequest(input_text="What is the risk?", expected_output="The risk is moderate.", actual_output="The risk is moderate.", references=["policy"])]
            )
        )
    )
    assert evaluation.scorecard["overall_quality"] >= 0


def test_reasoning_risk_projection_has_projection() -> None:
    service = ReasoningService(repository=ReasoningRepository(), settings=TestingSettings(), redis_client=None, logger=logging.getLogger("test"))
    result = __import__("asyncio").run(service.risk_project(RiskAnalyzeRequest(query="Check supply chain risk", risk_factors=["supplier fragility"], assets=["prod-api"], dependencies=["third-party-auth"])))
    assert result.projected_risk >= result.current_risk
