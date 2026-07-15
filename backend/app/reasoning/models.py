from __future__ import annotations

from uuid import UUID

from sqlalchemy import Boolean, Float, ForeignKey, Integer, JSON, String, Text
from sqlalchemy import Uuid
from sqlalchemy.orm import Mapped, mapped_column

from app.database.models.base import BaseModel, TimestampMixin, UUIDMixin


class ReasoningTrace(BaseModel, UUIDMixin, TimestampMixin):
    __tablename__ = "reasoning_traces"

    query: Mapped[str] = mapped_column(Text, nullable=False)
    decision_type: Mapped[str] = mapped_column(String(64), nullable=False, default="analysis")
    strategy: Mapped[str] = mapped_column(String(64), nullable=False, default="hybrid")
    decision_summary: Mapped[str] = mapped_column(Text, nullable=False, default="")
    decision_graph: Mapped[list[dict[str, object]]] = mapped_column(JSON, nullable=False, default=list)
    reasoning_steps: Mapped[list[str]] = mapped_column(JSON, nullable=False, default=list)
    source_references: Mapped[list[str]] = mapped_column(JSON, nullable=False, default=list)
    knowledge_sources: Mapped[list[str]] = mapped_column(JSON, nullable=False, default=list)
    mitre_references: Mapped[list[str]] = mapped_column(JSON, nullable=False, default=list)
    compliance_references: Mapped[list[str]] = mapped_column(JSON, nullable=False, default=list)
    risk_level: Mapped[str] = mapped_column(String(32), nullable=False, default="moderate")
    business_impact: Mapped[str] = mapped_column(String(1024), nullable=False, default="")
    technical_impact: Mapped[str] = mapped_column(String(1024), nullable=False, default="")
    limitations: Mapped[list[str]] = mapped_column(JSON, nullable=False, default=list)
    recommended_actions: Mapped[list[str]] = mapped_column(JSON, nullable=False, default=list)
    alternative_actions: Mapped[list[str]] = mapped_column(JSON, nullable=False, default=list)
    decision_metadata: Mapped[dict[str, object]] = mapped_column(JSON, nullable=False, default=dict)
    scorecard: Mapped[dict[str, float]] = mapped_column(JSON, nullable=False, default=dict)
    input_context: Mapped[dict[str, object]] = mapped_column(JSON, nullable=False, default=dict)
    output_context: Mapped[dict[str, object]] = mapped_column(JSON, nullable=False, default=dict)


class DecisionRecord(BaseModel, UUIDMixin, TimestampMixin):
    __tablename__ = "decision_records"

    trace_id: Mapped[UUID | None] = mapped_column(Uuid(as_uuid=True), ForeignKey("reasoning_traces.id", ondelete="SET NULL"), nullable=True, index=True)
    decision_key: Mapped[str] = mapped_column(String(128), nullable=False, index=True)
    decision_type: Mapped[str] = mapped_column(String(64), nullable=False, default="analysis")
    decision_summary: Mapped[str] = mapped_column(Text, nullable=False, default="")
    decision_payload: Mapped[dict[str, object]] = mapped_column(JSON, nullable=False, default=dict)
    decision_version: Mapped[int] = mapped_column(Integer, nullable=False, default=1)
    comparison_payload: Mapped[dict[str, object]] = mapped_column(JSON, nullable=False, default=dict)
    status: Mapped[str] = mapped_column(String(32), nullable=False, default="draft")
    confidence_score: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    trust_score: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    risk_level: Mapped[str] = mapped_column(String(32), nullable=False, default="moderate")
    business_impact: Mapped[str] = mapped_column(String(1024), nullable=False, default="")
    technical_impact: Mapped[str] = mapped_column(String(1024), nullable=False, default="")
    rollback_of: Mapped[UUID | None] = mapped_column(Uuid(as_uuid=True), nullable=True)
    decision_metadata: Mapped[dict[str, object]] = mapped_column(JSON, nullable=False, default=dict)


class EvidenceRecord(BaseModel, UUIDMixin, TimestampMixin):
    __tablename__ = "evidence_records"

    trace_id: Mapped[UUID | None] = mapped_column(Uuid(as_uuid=True), ForeignKey("reasoning_traces.id", ondelete="SET NULL"), nullable=True, index=True)
    decision_id: Mapped[UUID | None] = mapped_column(Uuid(as_uuid=True), ForeignKey("decision_records.id", ondelete="SET NULL"), nullable=True, index=True)
    source_type: Mapped[str] = mapped_column(String(64), nullable=False)
    source_name: Mapped[str] = mapped_column(String(255), nullable=False)
    claim: Mapped[str] = mapped_column(Text, nullable=False)
    snippet: Mapped[str | None] = mapped_column(Text, nullable=True)
    reference_uri: Mapped[str | None] = mapped_column(String(1024), nullable=True)
    score: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    verified: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    evidence_metadata: Mapped[dict[str, object]] = mapped_column(JSON, nullable=False, default=dict)


class TrustScore(BaseModel, UUIDMixin, TimestampMixin):
    __tablename__ = "trust_scores"

    trace_id: Mapped[UUID | None] = mapped_column(Uuid(as_uuid=True), ForeignKey("reasoning_traces.id", ondelete="SET NULL"), nullable=True, index=True)
    decision_id: Mapped[UUID | None] = mapped_column(Uuid(as_uuid=True), ForeignKey("decision_records.id", ondelete="SET NULL"), nullable=True, index=True)
    evidence_trust: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    knowledge_trust: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    reasoning_trust: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    source_trust: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    decision_trust: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    agent_trust: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    model_trust: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    overall_trust: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    trust_metadata: Mapped[dict[str, object]] = mapped_column(JSON, nullable=False, default=dict)


class ConfidenceScore(BaseModel, UUIDMixin, TimestampMixin):
    __tablename__ = "confidence_scores"

    trace_id: Mapped[UUID | None] = mapped_column(Uuid(as_uuid=True), ForeignKey("reasoning_traces.id", ondelete="SET NULL"), nullable=True, index=True)
    decision_id: Mapped[UUID | None] = mapped_column(Uuid(as_uuid=True), ForeignKey("decision_records.id", ondelete="SET NULL"), nullable=True, index=True)
    evidence_strength: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    knowledge_score: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    model_score: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    reasoning_score: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    data_quality_score: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    risk_confidence: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    decision_confidence: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    overall_confidence: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    confidence_metadata: Mapped[dict[str, object]] = mapped_column(JSON, nullable=False, default=dict)


class Recommendation(BaseModel, UUIDMixin, TimestampMixin):
    __tablename__ = "recommendations"

    trace_id: Mapped[UUID | None] = mapped_column(Uuid(as_uuid=True), ForeignKey("reasoning_traces.id", ondelete="SET NULL"), nullable=True, index=True)
    decision_id: Mapped[UUID | None] = mapped_column(Uuid(as_uuid=True), ForeignKey("decision_records.id", ondelete="SET NULL"), nullable=True, index=True)
    priority_rank: Mapped[int] = mapped_column(Integer, nullable=False, default=1)
    category: Mapped[str] = mapped_column(String(64), nullable=False, default="business")
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    action: Mapped[str] = mapped_column(Text, nullable=False)
    horizon: Mapped[str] = mapped_column(String(32), nullable=False, default="immediate")
    expected_impact: Mapped[str] = mapped_column(Text, nullable=False, default="")
    business_value: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    technical_value: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    security_value: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    compliance_value: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    recommendation_metadata: Mapped[dict[str, object]] = mapped_column(JSON, nullable=False, default=dict)


class RiskProjection(BaseModel, UUIDMixin, TimestampMixin):
    __tablename__ = "risk_projections"

    trace_id: Mapped[UUID | None] = mapped_column(Uuid(as_uuid=True), ForeignKey("reasoning_traces.id", ondelete="SET NULL"), nullable=True, index=True)
    decision_id: Mapped[UUID | None] = mapped_column(Uuid(as_uuid=True), ForeignKey("decision_records.id", ondelete="SET NULL"), nullable=True, index=True)
    risk_level: Mapped[str] = mapped_column(String(32), nullable=False, default="moderate")
    current_risk: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    technical_risk: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    operational_risk: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    business_risk: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    financial_risk: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    compliance_risk: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    reputation_risk: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    infrastructure_risk: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    identity_risk: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    cloud_risk: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    ai_risk: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    supply_chain_risk: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    risk_breakdown: Mapped[dict[str, float]] = mapped_column(JSON, nullable=False, default=dict)
    business_impact: Mapped[str] = mapped_column(String(1024), nullable=False, default="")
    technical_impact: Mapped[str] = mapped_column(String(1024), nullable=False, default="")
    risk_metadata: Mapped[dict[str, object]] = mapped_column(JSON, nullable=False, default=dict)


class EvaluationRun(BaseModel, UUIDMixin, TimestampMixin):
    __tablename__ = "evaluation_runs"

    trace_id: Mapped[UUID | None] = mapped_column(Uuid(as_uuid=True), ForeignKey("reasoning_traces.id", ondelete="SET NULL"), nullable=True, index=True)
    dataset_name: Mapped[str] = mapped_column(String(255), nullable=False)
    benchmark_name: Mapped[str] = mapped_column(String(255), nullable=False, default="enterprise-reasoning")
    model_name: Mapped[str] = mapped_column(String(255), nullable=False)
    status: Mapped[str] = mapped_column(String(32), nullable=False, default="completed")
    scorecard: Mapped[dict[str, float]] = mapped_column(JSON, nullable=False, default=dict)
    evaluation_metadata: Mapped[dict[str, object]] = mapped_column(JSON, nullable=False, default=dict)


class EvaluationMetric(BaseModel, UUIDMixin, TimestampMixin):
    __tablename__ = "evaluation_metrics"

    run_id: Mapped[UUID | None] = mapped_column(Uuid(as_uuid=True), ForeignKey("evaluation_runs.id", ondelete="SET NULL"), nullable=True, index=True)
    metric_name: Mapped[str] = mapped_column(String(128), nullable=False)
    metric_value: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    benchmark_value: Mapped[float | None] = mapped_column(Float, nullable=True)
    target_value: Mapped[float | None] = mapped_column(Float, nullable=True)
    passed: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    metric_metadata: Mapped[dict[str, object]] = mapped_column(JSON, nullable=False, default=dict)


class HallucinationRecord(BaseModel, UUIDMixin, TimestampMixin):
    __tablename__ = "hallucination_records"

    trace_id: Mapped[UUID | None] = mapped_column(Uuid(as_uuid=True), ForeignKey("reasoning_traces.id", ondelete="SET NULL"), nullable=True, index=True)
    decision_id: Mapped[UUID | None] = mapped_column(Uuid(as_uuid=True), ForeignKey("decision_records.id", ondelete="SET NULL"), nullable=True, index=True)
    unsupported_claims: Mapped[list[str]] = mapped_column(JSON, nullable=False, default=list)
    fact_verification: Mapped[str] = mapped_column(String(64), nullable=False, default="unknown")
    reference_validation: Mapped[str] = mapped_column(String(64), nullable=False, default="unknown")
    confidence_penalty: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    response_verified: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    hallucination_metadata: Mapped[dict[str, object]] = mapped_column(JSON, nullable=False, default=dict)
