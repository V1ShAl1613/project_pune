from __future__ import annotations

import logging

from app.core.settings import TestingSettings
from app.executive.dependencies import provide_executive_service
from app.executive.services.executive_service import ExecutiveService


class _FakeExecutiveService:
    def __init__(self) -> None:
        self.service = ExecutiveService(settings=TestingSettings(), redis_client=None, logger=logging.getLogger("test"))

    async def overview(self):
        return await self.service.overview()

    async def kpis(self):
        return await self.service.kpis()

    async def trends(self):
        return await self.service.trends()

    async def reports(self):
        return await self.service.reports()

    async def report(self, report_code: str):
        return await self.service.report(report_code)

    async def forecasts(self):
        return await self.service.forecasts()

    async def recommendations(self):
        return await self.service.recommendations()

    async def decisions(self):
        return await self.service.decisions()


def test_executive_routes_are_registered(client, app) -> None:
    app.dependency_overrides[provide_executive_service] = lambda: _FakeExecutiveService()
    try:
        overview_response = client.get("/api/v1/executive/overview")
        kpis_response = client.get("/api/v1/executive/kpis")
        reports_response = client.get("/api/v1/executive/reports")
        report_response = client.get("/api/v1/executive/reports/RPT-BOARD-001")
        recommendations_response = client.get("/api/v1/executive/recommendations")
        decisions_response = client.get("/api/v1/executive/decisions")
    finally:
        app.dependency_overrides.clear()

    assert overview_response.status_code == 200
    assert kpis_response.status_code == 200
    assert reports_response.status_code == 200
    assert report_response.status_code == 200
    assert recommendations_response.status_code == 200
    assert decisions_response.status_code == 200
    assert overview_response.json()["summary"]["operating_status"] == "operational"
    assert kpis_response.json()[0]["code"]
    assert reports_response.json()[0]["report_code"] == "RPT-BOARD-001"
    assert recommendations_response.json()[0]["priority"] in {"critical", "high", "medium", "low"}
