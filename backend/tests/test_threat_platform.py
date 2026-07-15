from __future__ import annotations

import logging

from app.core.settings import TestingSettings
from app.threat.dependencies import provide_threat_service
from app.threat.repositories.threat_repository import ThreatRepository
from app.threat.schemas import AttackPathAnalyzeRequest, GraphPathRequest, GraphQueryRequest, GraphQueryType, IOCSearchRequest, IOCType, ThreatAnalysisRequest, ThreatHuntRequest, ThreatHuntType
from app.threat.services.threat_service import ThreatService


class _FakeThreatService:
    def __init__(self) -> None:
        self.service = ThreatService(repository=ThreatRepository(), settings=TestingSettings(), redis_client=None, logger=logging.getLogger("test"))

    async def analyze(self, payload):
        return await self.service.analyze(payload)

    async def correlate(self, payload):
        return await self.service.correlate(payload)

    async def hunt(self, payload):
        return await self.service.hunt(payload)

    async def list_actors(self):
        return []

    async def list_campaigns(self):
        return []

    async def mitre_matrix(self, query=None):
        return await self.service.mitre_matrix(query=query)

    async def graph_query(self, payload):
        return await self.service.graph_query(payload)

    async def graph_path(self, payload):
        return await self.service.graph_path(payload)

    async def list_iocs(self):
        return []

    async def search_iocs(self, payload):
        return []

    async def attack_paths(self, payload):
        return await self.service.attack_paths(payload)

    async def metrics(self):
        return await self.service.metrics()


def test_threat_analyze_route_is_registered(client, app) -> None:
    app.dependency_overrides[provide_threat_service] = lambda: _FakeThreatService()
    try:
        response = client.post(
            "/threats/analyze",
            json={
                "query": "Suspicious phishing to cloud token abuse",
                "iocs": ["evil.example.com", "https://example.invalid/payload"],
                "assets": ["prod-api", "cloud-auth"],
                "users": ["alice@example.com"],
                "source_references": ["https://example.invalid/report"],
                "mitre_techniques": ["T1566"],
            },
        )
    finally:
        app.dependency_overrides.clear()

    assert response.status_code == 200
    payload = response.json()
    assert payload["query"] == "Suspicious phishing to cloud token abuse"
    assert payload["confidence"] >= 0
    assert payload["kill_chain_stage"] in {"reconnaissance", "delivery", "exploitation", "installation", "command_and_control", "actions_on_objectives", "weaponization"}


def test_threat_hunt_returns_findings() -> None:
    service = ThreatService(repository=ThreatRepository(), settings=TestingSettings(), redis_client=None, logger=logging.getLogger("test"))
    result = __import__("asyncio").run(
        service.hunt(
            ThreatHuntRequest(
                query="hunt for suspicious login abuse",
                hunt_type=ThreatHuntType.IDENTITY,
                iocs=["198.51.100.25", "bad.example.com"],
                assets=["identity-provider"],
                users=["user@example.com"],
            )
        )
    )
    assert result.findings
    assert result.confidence >= 0


def test_graph_path_analysis_returns_path() -> None:
    service = ThreatService(repository=ThreatRepository(), settings=TestingSettings(), redis_client=None, logger=logging.getLogger("test"))
    __import__("asyncio").run(
        service.graph_query(
            GraphQueryRequest(
                query="build graph",
                query_type=GraphQueryType.TRAVERSAL,
                context={},
            )
        )
    )
    result = __import__("asyncio").run(service.graph_path(GraphPathRequest(source="alpha", target="omega")))
    assert isinstance(result["shortest_path"], list)


def test_attack_path_analysis_produces_chain() -> None:
    service = ThreatService(repository=ThreatRepository(), settings=TestingSettings(), redis_client=None, logger=logging.getLogger("test"))
    result = __import__("asyncio").run(
        service.attack_paths(
            AttackPathAnalyzeRequest(source_asset="prod-api", target_asset="data-vault", assets=["prod-api", "data-vault"])
        )
    )
    assert result.attack_chain
    assert result.confidence >= 0


def test_ioc_search_route_is_registered(client, app) -> None:
    app.dependency_overrides[provide_threat_service] = lambda: _FakeThreatService()
    try:
        response = client.post(
            "/iocs/search",
            json={"query": "example", "indicator_type": IOCType.DOMAIN.value, "limit": 5},
        )
    finally:
        app.dependency_overrides.clear()

    assert response.status_code == 200
    assert isinstance(response.json(), list)
