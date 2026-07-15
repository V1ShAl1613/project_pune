from __future__ import annotations

from datetime import datetime
from enum import StrEnum

from pydantic import BaseModel, ConfigDict, Field


class ExecutivePriority(StrEnum):
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


class ExecutiveTrendDirection(StrEnum):
    UP = "up"
    FLAT = "flat"
    DOWN = "down"


class ExecutiveKPIResponse(BaseModel):
    model_config = ConfigDict(extra="forbid", from_attributes=True, protected_namespaces=())

    code: str
    label: str
    value: str
    unit: str | None = None
    delta: str | None = None
    direction: ExecutiveTrendDirection = ExecutiveTrendDirection.FLAT
    benchmark: str | None = None
    detail: str = ""
    category: str = "enterprise"


class ExecutiveTrendPointResponse(BaseModel):
    model_config = ConfigDict(extra="forbid", from_attributes=True, protected_namespaces=())

    label: str
    value: float


class ExecutiveTrendResponse(BaseModel):
    model_config = ConfigDict(extra="forbid", from_attributes=True, protected_namespaces=())

    code: str
    label: str
    category: str
    summary: str
    points: list[ExecutiveTrendPointResponse] = Field(default_factory=list)


class ExecutiveReportResponse(BaseModel):
    model_config = ConfigDict(extra="forbid", from_attributes=True, protected_namespaces=())

    report_code: str
    title: str
    audience: str
    owner: str
    status: str
    score: float
    summary: str
    highlights: list[str] = Field(default_factory=list)
    period_label: str
    published_at: datetime | None = None
    report_metadata: dict[str, object] = Field(default_factory=dict)


class ExecutiveForecastResponse(BaseModel):
    model_config = ConfigDict(extra="forbid", from_attributes=True, protected_namespaces=())

    scenario: str
    horizon: str
    confidence: float
    projected_value: str
    lower_bound: str
    upper_bound: str
    drivers: list[str] = Field(default_factory=list)
    forecast_metadata: dict[str, object] = Field(default_factory=dict)


class ExecutiveRecommendationResponse(BaseModel):
    model_config = ConfigDict(extra="forbid", from_attributes=True, protected_namespaces=())

    priority_rank: int
    priority: ExecutivePriority
    title: str
    action: str
    owner: str
    horizon: str
    expected_impact: str
    value_score: float
    evidence: list[str] = Field(default_factory=list)
    recommendation_metadata: dict[str, object] = Field(default_factory=dict)


class ExecutiveDecisionResponse(BaseModel):
    model_config = ConfigDict(extra="forbid", from_attributes=True, protected_namespaces=())

    decision_code: str
    topic: str
    decision: str
    status: str
    approved_by: str | None = None
    rationale: str
    impact: str
    next_review_at: datetime | None = None
    decision_metadata: dict[str, object] = Field(default_factory=dict)


class ExecutiveSummaryResponse(BaseModel):
    model_config = ConfigDict(extra="forbid", from_attributes=True, protected_namespaces=())

    title: str
    narrative: str
    operating_status: str
    health_score: float
    decision_velocity: str
    risk_posture: str


class ExecutiveOverviewResponse(BaseModel):
    model_config = ConfigDict(extra="forbid", from_attributes=True, protected_namespaces=())

    generated_at: datetime
    summary: ExecutiveSummaryResponse
    kpis: list[ExecutiveKPIResponse] = Field(default_factory=list)
    trends: list[ExecutiveTrendResponse] = Field(default_factory=list)
    reports: list[ExecutiveReportResponse] = Field(default_factory=list)
    forecasts: list[ExecutiveForecastResponse] = Field(default_factory=list)
    recommendations: list[ExecutiveRecommendationResponse] = Field(default_factory=list)
    decisions: list[ExecutiveDecisionResponse] = Field(default_factory=list)
