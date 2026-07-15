from __future__ import annotations

from datetime import datetime
from uuid import UUID

from sqlalchemy import DateTime, Float, ForeignKey, Integer, JSON, String, Text
from sqlalchemy import Uuid
from sqlalchemy.orm import Mapped, mapped_column

from app.database.models.base import BaseModel, TimestampMixin, UUIDMixin


class ExecutiveDashboard(BaseModel, UUIDMixin, TimestampMixin):
    __tablename__ = "executive_dashboards"

    code: Mapped[str] = mapped_column(String(64), nullable=False, unique=True, index=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    owner: Mapped[str] = mapped_column(String(255), nullable=False, default="executive-office")
    status: Mapped[str] = mapped_column(String(32), nullable=False, default="active")
    dashboard_metadata: Mapped[dict[str, object]] = mapped_column(JSON, nullable=False, default=dict)


class ExecutiveKPI(BaseModel, UUIDMixin, TimestampMixin):
    __tablename__ = "executive_kpis"

    dashboard_id: Mapped[UUID | None] = mapped_column(Uuid(as_uuid=True), ForeignKey("executive_dashboards.id", ondelete="SET NULL"), nullable=True, index=True)
    code: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    label: Mapped[str] = mapped_column(String(255), nullable=False)
    value: Mapped[str] = mapped_column(String(64), nullable=False)
    unit: Mapped[str | None] = mapped_column(String(32), nullable=True)
    delta: Mapped[str | None] = mapped_column(String(32), nullable=True)
    direction: Mapped[str] = mapped_column(String(16), nullable=False, default="flat")
    benchmark: Mapped[str | None] = mapped_column(String(64), nullable=True)
    detail: Mapped[str] = mapped_column(Text, nullable=False, default="")
    kpi_metadata: Mapped[dict[str, object]] = mapped_column(JSON, nullable=False, default=dict)


class ExecutiveTrend(BaseModel, UUIDMixin, TimestampMixin):
    __tablename__ = "executive_trends"

    dashboard_id: Mapped[UUID | None] = mapped_column(Uuid(as_uuid=True), ForeignKey("executive_dashboards.id", ondelete="SET NULL"), nullable=True, index=True)
    code: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    label: Mapped[str] = mapped_column(String(255), nullable=False)
    category: Mapped[str] = mapped_column(String(64), nullable=False, default="enterprise")
    summary: Mapped[str] = mapped_column(Text, nullable=False, default="")
    trend_points: Mapped[list[dict[str, object]]] = mapped_column(JSON, nullable=False, default=list)
    trend_metadata: Mapped[dict[str, object]] = mapped_column(JSON, nullable=False, default=dict)


class ExecutiveReport(BaseModel, UUIDMixin, TimestampMixin):
    __tablename__ = "executive_reports"

    dashboard_id: Mapped[UUID | None] = mapped_column(Uuid(as_uuid=True), ForeignKey("executive_dashboards.id", ondelete="SET NULL"), nullable=True, index=True)
    report_code: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    audience: Mapped[str] = mapped_column(String(128), nullable=False)
    owner: Mapped[str] = mapped_column(String(255), nullable=False)
    status: Mapped[str] = mapped_column(String(32), nullable=False, default="published")
    score: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    summary: Mapped[str] = mapped_column(Text, nullable=False, default="")
    highlights: Mapped[list[str]] = mapped_column(JSON, nullable=False, default=list)
    period_label: Mapped[str] = mapped_column(String(64), nullable=False, default="Q1")
    published_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    report_metadata: Mapped[dict[str, object]] = mapped_column(JSON, nullable=False, default=dict)


class ExecutiveForecast(BaseModel, UUIDMixin, TimestampMixin):
    __tablename__ = "executive_forecasts"

    dashboard_id: Mapped[UUID | None] = mapped_column(Uuid(as_uuid=True), ForeignKey("executive_dashboards.id", ondelete="SET NULL"), nullable=True, index=True)
    scenario: Mapped[str] = mapped_column(String(128), nullable=False)
    horizon: Mapped[str] = mapped_column(String(64), nullable=False)
    confidence: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    projected_value: Mapped[str] = mapped_column(String(64), nullable=False)
    lower_bound: Mapped[str] = mapped_column(String(64), nullable=False)
    upper_bound: Mapped[str] = mapped_column(String(64), nullable=False)
    drivers: Mapped[list[str]] = mapped_column(JSON, nullable=False, default=list)
    forecast_metadata: Mapped[dict[str, object]] = mapped_column(JSON, nullable=False, default=dict)


class ExecutiveRecommendation(BaseModel, UUIDMixin, TimestampMixin):
    __tablename__ = "executive_recommendations"

    dashboard_id: Mapped[UUID | None] = mapped_column(Uuid(as_uuid=True), ForeignKey("executive_dashboards.id", ondelete="SET NULL"), nullable=True, index=True)
    priority_rank: Mapped[int] = mapped_column(Integer, nullable=False, default=1)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    action: Mapped[str] = mapped_column(Text, nullable=False)
    owner: Mapped[str] = mapped_column(String(255), nullable=False)
    horizon: Mapped[str] = mapped_column(String(64), nullable=False)
    expected_impact: Mapped[str] = mapped_column(Text, nullable=False, default="")
    value_score: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    evidence: Mapped[list[str]] = mapped_column(JSON, nullable=False, default=list)
    recommendation_metadata: Mapped[dict[str, object]] = mapped_column(JSON, nullable=False, default=dict)


class ExecutiveDecision(BaseModel, UUIDMixin, TimestampMixin):
    __tablename__ = "executive_decisions"

    dashboard_id: Mapped[UUID | None] = mapped_column(Uuid(as_uuid=True), ForeignKey("executive_dashboards.id", ondelete="SET NULL"), nullable=True, index=True)
    decision_code: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    topic: Mapped[str] = mapped_column(String(255), nullable=False)
    decision: Mapped[str] = mapped_column(Text, nullable=False)
    status: Mapped[str] = mapped_column(String(32), nullable=False, default="proposed")
    approved_by: Mapped[str | None] = mapped_column(String(255), nullable=True)
    rationale: Mapped[str] = mapped_column(Text, nullable=False, default="")
    impact: Mapped[str] = mapped_column(Text, nullable=False, default="")
    next_review_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    decision_metadata: Mapped[dict[str, object]] = mapped_column(JSON, nullable=False, default=dict)
