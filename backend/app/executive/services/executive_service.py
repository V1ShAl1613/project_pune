from __future__ import annotations

import json
import logging
from dataclasses import dataclass
from datetime import UTC, datetime, timedelta

from redis.asyncio import Redis

from app.core.settings import AppSettings
from app.exceptions.base import BaseApplicationException
from app.executive.schemas import (
    ExecutiveDecisionResponse,
    ExecutiveForecastResponse,
    ExecutiveKPIResponse,
    ExecutiveOverviewResponse,
    ExecutivePriority,
    ExecutiveRecommendationResponse,
    ExecutiveReportResponse,
    ExecutiveSummaryResponse,
    ExecutiveTrendDirection,
    ExecutiveTrendPointResponse,
    ExecutiveTrendResponse,
)


@dataclass(slots=True)
class ExecutiveService:
    """Deterministic executive intelligence, analytics, and decision-support service."""

    settings: AppSettings
    redis_client: Redis | None
    logger: logging.Logger
    _overview: ExecutiveOverviewResponse | None = None

    def __post_init__(self) -> None:
        now = datetime.now(UTC)
        self._overview = ExecutiveOverviewResponse(
            generated_at=now,
            summary=ExecutiveSummaryResponse(
                title="Enterprise executive intelligence",
                narrative="Operational visibility, reporting, and decision support are consolidated into one executive view.",
                operating_status="operational",
                health_score=96.8,
                decision_velocity="2.4 days",
                risk_posture="controlled",
            ),
            kpis=[
                ExecutiveKPIResponse(code="kpi-revenue", label="Revenue protection", value="$128.4M", unit="USD", delta="+8.4%", direction=ExecutiveTrendDirection.UP, benchmark="$120.0M", detail="Recurring revenue is above plan and within executive target bands."),
                ExecutiveKPIResponse(code="kpi-margin", label="Operating margin", value="32.7%", unit="percent", delta="+1.2 pts", direction=ExecutiveTrendDirection.UP, benchmark="31.0%", detail="Margin expansion is being preserved across the current portfolio."),
                ExecutiveKPIResponse(code="kpi-risk", label="Strategic risk exposure", value="18", unit="index", delta="-4", direction=ExecutiveTrendDirection.DOWN, benchmark="24", detail="The weighted risk posture continues to fall as controls and decisions stabilize."),
                ExecutiveKPIResponse(code="kpi-speed", label="Decision cycle time", value="2.4 days", unit="days", delta="-0.6 day", direction=ExecutiveTrendDirection.DOWN, benchmark="3.5 days", detail="Executive approvals and follow-ups are moving faster than the baseline."),
                ExecutiveKPIResponse(code="kpi-portfolio", label="Portfolio coverage", value="94%", unit="percent", delta="+3 pts", direction=ExecutiveTrendDirection.UP, benchmark="90%", detail="Priority initiatives remain covered by reporting and review cadences."),
                ExecutiveKPIResponse(code="kpi-readiness", label="Board readiness", value="98%", unit="percent", delta="+2 pts", direction=ExecutiveTrendDirection.UP, benchmark="95%", detail="Executive packs are current and ready for stakeholder review."),
            ],
            trends=[
                ExecutiveTrendResponse(
                    code="trend-performance",
                    label="Performance trend",
                    category="financial",
                    summary="Financial performance has accelerated over the last four review periods.",
                    points=[
                        ExecutiveTrendPointResponse(label="W1", value=82),
                        ExecutiveTrendPointResponse(label="W2", value=86),
                        ExecutiveTrendPointResponse(label="W3", value=91),
                        ExecutiveTrendPointResponse(label="W4", value=96),
                    ],
                ),
                ExecutiveTrendResponse(
                    code="trend-risk",
                    label="Risk burn-down",
                    category="risk",
                    summary="Residual risk is declining due to faster remediation and higher control adoption.",
                    points=[
                        ExecutiveTrendPointResponse(label="W1", value=28),
                        ExecutiveTrendPointResponse(label="W2", value=25),
                        ExecutiveTrendPointResponse(label="W3", value=21),
                        ExecutiveTrendPointResponse(label="W4", value=18),
                    ],
                ),
                ExecutiveTrendResponse(
                    code="trend-decisions",
                    label="Decision throughput",
                    category="operations",
                    summary="Decision throughput improved as escalation paths were simplified.",
                    points=[
                        ExecutiveTrendPointResponse(label="W1", value=14),
                        ExecutiveTrendPointResponse(label="W2", value=16),
                        ExecutiveTrendPointResponse(label="W3", value=18),
                        ExecutiveTrendPointResponse(label="W4", value=22),
                    ],
                ),
            ],
            reports=[
                ExecutiveReportResponse(report_code="RPT-BOARD-001", title="Board pack - enterprise health", audience="Board", owner="Office of the CFO", status="published", score=97.2, summary="Latest board pack synthesizes revenue, risk, and operating performance.", highlights=["Revenue above target", "Risk posture controlled", "Executive readiness green"], period_label="Q4", published_at=now - timedelta(days=2), report_metadata={"format": "board-pack", "pages": 18}),
                ExecutiveReportResponse(report_code="RPT-OPS-002", title="Operating review - portfolio execution", audience="Executive", owner="Chief Operating Office", status="published", score=95.4, summary="Portfolio execution remains stable with strong delivery cadence.", highlights=["Milestones on track", "Dependencies resolved", "Actions closed faster"], period_label="Month 08", published_at=now - timedelta(days=1), report_metadata={"format": "operations-review", "pages": 12}),
                ExecutiveReportResponse(report_code="RPT-RISK-003", title="Risk and resilience dashboard", audience="Risk Committee", owner="Chief Risk Office", status="published", score=93.8, summary="Enterprise risk is under threshold and improving steadily.", highlights=["Top risks bounded", "Control adoption increased", "Residual risk down"], period_label="Weekly", published_at=now - timedelta(hours=12), report_metadata={"format": "risk-dashboard", "pages": 9}),
                ExecutiveReportResponse(report_code="RPT-GROWTH-004", title="Growth and market expansion review", audience="Leadership", owner="Strategy Office", status="draft", score=91.1, summary="Expansion opportunities are pre-qualified and ready for leadership decision.", highlights=["New market fit", "Pipeline acceleration", "Investment gates defined"], period_label="Planning cycle", published_at=None, report_metadata={"format": "growth-review", "pages": 11}),
            ],
            forecasts=[
                ExecutiveForecastResponse(scenario="Base case", horizon="90 days", confidence=0.91, projected_value="$141.2M", lower_bound="$136.1M", upper_bound="$146.5M", drivers=["Current pipeline", "Retention improvement", "Delivery stability"], forecast_metadata={"model": "ensemble-v3"}),
                ExecutiveForecastResponse(scenario="Upside case", horizon="90 days", confidence=0.78, projected_value="$148.9M", lower_bound="$144.0M", upper_bound="$154.2M", drivers=["Commercial conversion", "Cross-sell", "Program acceleration"], forecast_metadata={"model": "ensemble-v3"}),
                ExecutiveForecastResponse(scenario="Downside case", horizon="90 days", confidence=0.66, projected_value="$133.8M", lower_bound="$129.4M", upper_bound="$138.0M", drivers=["Delay risk", "Market softness", "Execution drift"], forecast_metadata={"model": "ensemble-v3"}),
            ],
            recommendations=[
                ExecutiveRecommendationResponse(priority_rank=1, priority=ExecutivePriority.CRITICAL, title="Lock executive sponsor ownership for top initiatives", action="Assign accountable sponsors and review weekly until closure.", owner="Chief of Staff", horizon="Immediate", expected_impact="Accelerates decision closure and reduces stalled work.", value_score=98.4, evidence=["High-value initiatives still waiting on approvals", "Throughput improves when owner and due date are explicit"], recommendation_metadata={"category": "governance"}),
                ExecutiveRecommendationResponse(priority_rank=2, priority=ExecutivePriority.HIGH, title="Publish a board-ready reporting cadence", action="Freeze the reporting template and automate weekly distribution.", owner="Finance Operations", horizon="2 weeks", expected_impact="Improves executive visibility and removes ad hoc reporting effort.", value_score=95.1, evidence=["Board pack is already current", "Templates can be reused across committees"], recommendation_metadata={"category": "reporting"}),
                ExecutiveRecommendationResponse(priority_rank=3, priority=ExecutivePriority.HIGH, title="Expand scenario monitoring for downside risks", action="Track risk triggers and update forecast thresholds automatically.", owner="Risk Office", horizon="30 days", expected_impact="Strengthens early-warning coverage for strategic risk.", value_score=92.7, evidence=["Risk burn-down is improving", "Forecast confidence depends on timely threshold alerts"], recommendation_metadata={"category": "risk"}),
                ExecutiveRecommendationResponse(priority_rank=4, priority=ExecutivePriority.MEDIUM, title="Standardize decision logs across business units", action="Require every executive decision to capture rationale, owner, and follow-up date.", owner="Program Management Office", horizon="30 days", expected_impact="Creates a reusable decision history for future executive review.", value_score=88.6, evidence=["Decision velocity is a strong leading indicator", "Auditability improves when decision logs are consistent"], recommendation_metadata={"category": "decision-support"}),
            ],
            decisions=[
                ExecutiveDecisionResponse(decision_code="DEC-2025-001", topic="Portfolio investment mix", decision="Proceed with the current investment allocation and continue quarterly rebalancing.", status="approved", approved_by="Executive Committee", rationale="The current portfolio balances growth and resilience while maintaining margin discipline.", impact="Supports the planned growth trajectory without adding unnecessary operational exposure.", next_review_at=now + timedelta(days=30), decision_metadata={"vote": "unanimous"}),
                ExecutiveDecisionResponse(decision_code="DEC-2025-002", topic="Reporting simplification", decision="Consolidate duplicate executive dashboards into one operating view.", status="approved", approved_by="Chief Operating Officer", rationale="A single executive dashboard reduces reconciliation time and improves adoption.", impact="Removes reporting duplication and shortens prep cycles for leadership reviews.", next_review_at=now + timedelta(days=21), decision_metadata={"vote": "consensus"}),
                ExecutiveDecisionResponse(decision_code="DEC-2025-003", topic="Risk escalation threshold", decision="Lower the strategic escalation threshold for high-value initiatives.", status="in_progress", approved_by=None, rationale="A tighter escalation threshold should surface exceptions earlier in the planning cycle.", impact="Improves governance on critical initiatives and accelerates resolution.", next_review_at=now + timedelta(days=14), decision_metadata={"vote": "pending"}),
            ],
        )

    async def overview(self) -> ExecutiveOverviewResponse:
        cached = await self._cache_get("executive:overview")
        if cached is not None:
            return ExecutiveOverviewResponse.model_validate(cached)
        await self._cache_set("executive:overview", self._overview.model_dump(mode="json"), ttl=300)
        return self._overview

    async def kpis(self) -> list[ExecutiveKPIResponse]:
        overview = await self.overview()
        return overview.kpis

    async def trends(self) -> list[ExecutiveTrendResponse]:
        overview = await self.overview()
        return overview.trends

    async def reports(self) -> list[ExecutiveReportResponse]:
        overview = await self.overview()
        return overview.reports

    async def report(self, report_code: str) -> ExecutiveReportResponse:
        for report in await self.reports():
            if report.report_code == report_code:
                return report
        raise BaseApplicationException("Executive report not found", status_code=404, error_code="executive_report_not_found")

    async def forecasts(self) -> list[ExecutiveForecastResponse]:
        overview = await self.overview()
        return overview.forecasts

    async def recommendations(self) -> list[ExecutiveRecommendationResponse]:
        overview = await self.overview()
        return overview.recommendations

    async def decisions(self) -> list[ExecutiveDecisionResponse]:
        overview = await self.overview()
        return overview.decisions

    async def _cache_get(self, key: str) -> dict[str, object] | None:
        if self.redis_client is None:
            return None
        cached = await self.redis_client.get(key)
        if cached is None:
            return None
        if isinstance(cached, bytes):
            cached = cached.decode("utf-8")
        return json.loads(cached)

    async def _cache_set(self, key: str, value: dict[str, object], ttl: int) -> None:
        if self.redis_client is None:
            return
        await self.redis_client.set(key, json.dumps(value, default=str), ex=ttl)
