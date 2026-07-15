from __future__ import annotations

from datetime import datetime
from enum import StrEnum
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, field_validator


class ReasoningStrategy(StrEnum):
    SEQUENTIAL = "sequential"
    HIERARCHICAL = "hierarchical"
    RULE_BASED = "rule_based"
    GRAPH = "graph"
    HYBRID = "hybrid"
    EVIDENCE_BASED = "evidence_based"
    CONTEXT_AWARE = "context_aware"
    ITERATIVE_REFINEMENT = "iterative_refinement"
    REFLECTION = "reflection"
    SELF_VERIFICATION = "self_verification"


class ReasoningRequest(BaseModel):
    model_config = ConfigDict(extra="forbid", protected_namespaces=())

    query: str = Field(min_length=1, max_length=8192)
    strategy: ReasoningStrategy = ReasoningStrategy.HYBRID
    decision_type: str = Field(default="analysis", max_length=64)
    decision_domain: str = Field(default="enterprise", max_length=64)
    context: dict[str, object] = Field(default_factory=dict)
    evidence: list[dict[str, object]] = Field(default_factory=list)
    knowledge_sources: list[str] = Field(default_factory=list)
    mitre_references: list[str] = Field(default_factory=list)
    compliance_references: list[str] = Field(default_factory=list)
    source_references: list[str] = Field(default_factory=list)
    recommended_actions: list[str] = Field(default_factory=list)
    alternative_actions: list[str] = Field(default_factory=list)
    risk_factors: list[str] = Field(default_factory=list)
    business_context: str | None = None
    technical_context: str | None = None
    user_context: dict[str, object] = Field(default_factory=dict)
    workspace_context: dict[str, object] = Field(default_factory=dict)
    metadata: dict[str, object] = Field(default_factory=dict)

    @field_validator(
        "knowledge_sources",
        "mitre_references",
        "compliance_references",
        "source_references",
        "recommended_actions",
        "alternative_actions",
        "risk_factors",
    )
    @classmethod
    def _trim_list(cls, value: list[str]) -> list[str]:
        return [item.strip() for item in value if item and item.strip()]


class ReasoningValidateRequest(ReasoningRequest):
    confidence_threshold: int = Field(default=70, ge=0, le=100)
    trust_threshold: int = Field(default=70, ge=0, le=100)
    risk_threshold: int = Field(default=60, ge=0, le=100)
    policy_requirements: list[str] = Field(default_factory=list)
    knowledge_freshness_hours: int = Field(default=72, ge=1, le=8760)
    output_text: str | None = None


class EvaluationSampleRequest(BaseModel):
    model_config = ConfigDict(extra="forbid", protected_namespaces=())

    input_text: str = Field(min_length=1)
    expected_output: str = Field(min_length=1)
    actual_output: str = Field(default="")
    context: dict[str, object] = Field(default_factory=dict)
    references: list[str] = Field(default_factory=list)
    metadata: dict[str, object] = Field(default_factory=dict)


class ReasoningEvaluateRequest(BaseModel):
    model_config = ConfigDict(extra="forbid", protected_namespaces=())

    dataset_name: str = Field(min_length=1, max_length=255)
    benchmark_name: str = Field(default="enterprise-reasoning", max_length=255)
    model_name: str = Field(default="nvidia/nemotron-mini", max_length=255)
    samples: list[EvaluationSampleRequest] = Field(default_factory=list)
    metadata: dict[str, object] = Field(default_factory=dict)

    @field_validator("samples")
    @classmethod
    def _validate_samples(cls, value: list[EvaluationSampleRequest]) -> list[EvaluationSampleRequest]:
        if not value:
            raise ValueError("samples cannot be empty")
        return value


class RiskAnalyzeRequest(BaseModel):
    model_config = ConfigDict(extra="forbid", protected_namespaces=())

    query: str = Field(min_length=1, max_length=8192)
    current_risk: float = Field(default=50.0, ge=0.0, le=100.0)
    risk_factors: list[str] = Field(default_factory=list)
    assets: list[str] = Field(default_factory=list)
    dependencies: list[str] = Field(default_factory=list)
    context: dict[str, object] = Field(default_factory=dict)
    metadata: dict[str, object] = Field(default_factory=dict)


class RiskProjectRequest(RiskAnalyzeRequest):
    horizon_days: int = Field(default=30, ge=1, le=3650)


class EvidenceResponse(BaseModel):
    model_config = ConfigDict(extra="forbid", from_attributes=True, protected_namespaces=())

    id: UUID
    trace_id: UUID | None
    decision_id: UUID | None
    source_type: str
    source_name: str
    claim: str
    snippet: str | None
    reference_uri: str | None
    score: float
    verified: bool
    evidence_metadata: dict[str, object]
    created_at: datetime
    updated_at: datetime


class ConfidenceResponse(BaseModel):
    model_config = ConfigDict(extra="forbid", from_attributes=True, protected_namespaces=())

    id: UUID
    trace_id: UUID | None
    decision_id: UUID | None
    evidence_strength: float
    knowledge_score: float
    model_score: float
    reasoning_score: float
    data_quality_score: float
    risk_confidence: float
    decision_confidence: float
    overall_confidence: float
    confidence_metadata: dict[str, object]
    created_at: datetime
    updated_at: datetime


class TrustResponse(BaseModel):
    model_config = ConfigDict(extra="forbid", from_attributes=True, protected_namespaces=())

    id: UUID
    trace_id: UUID | None
    decision_id: UUID | None
    evidence_trust: float
    knowledge_trust: float
    reasoning_trust: float
    source_trust: float
    decision_trust: float
    agent_trust: float
    model_trust: float
    overall_trust: float
    trust_metadata: dict[str, object]
    created_at: datetime
    updated_at: datetime


class HallucinationResponse(BaseModel):
    model_config = ConfigDict(extra="forbid", from_attributes=True, protected_namespaces=())

    id: UUID
    trace_id: UUID | None
    decision_id: UUID | None
    unsupported_claims: list[str]
    fact_verification: str
    reference_validation: str
    confidence_penalty: float
    response_verified: bool
    hallucination_metadata: dict[str, object]
    created_at: datetime
    updated_at: datetime


class RiskAssessmentResponse(BaseModel):
    model_config = ConfigDict(extra="forbid", from_attributes=True, protected_namespaces=())

    id: UUID
    trace_id: UUID | None
    decision_id: UUID | None
    risk_level: str
    current_risk: float
    technical_risk: float
    operational_risk: float
    business_risk: float
    financial_risk: float
    compliance_risk: float
    reputation_risk: float
    infrastructure_risk: float
    identity_risk: float
    cloud_risk: float
    ai_risk: float
    supply_chain_risk: float
    risk_breakdown: dict[str, float]
    business_impact: str
    technical_impact: str
    risk_metadata: dict[str, object]
    created_at: datetime
    updated_at: datetime


class QuantumRiskProjectionResponse(BaseModel):
    model_config = ConfigDict(extra="forbid", from_attributes=True, protected_namespaces=())

    id: UUID
    trace_id: UUID | None
    decision_id: UUID | None
    current_risk: float
    projected_risk: float
    worst_case: float
    best_case: float
    likelihood: float
    exposure: float
    business_criticality: float
    recovery_difficulty: float
    confidence: float
    attack_chain: list[dict[str, object]]
    quantum_metadata: dict[str, object]
    created_at: datetime
    updated_at: datetime


class RecommendationResponse(BaseModel):
    model_config = ConfigDict(extra="forbid", from_attributes=True, protected_namespaces=())

    id: UUID
    trace_id: UUID | None
    decision_id: UUID | None
    priority_rank: int
    category: str
    title: str
    action: str
    horizon: str
    expected_impact: str
    business_value: float
    technical_value: float
    security_value: float
    compliance_value: float
    recommendation_metadata: dict[str, object]
    created_at: datetime
    updated_at: datetime


class DecisionValidationResponse(BaseModel):
    model_config = ConfigDict(extra="forbid", from_attributes=True, protected_namespaces=())

    id: UUID
    trace_id: UUID | None
    decision_id: UUID | None
    evidence_completeness: bool
    confidence_threshold_met: bool
    policy_compliance: bool
    knowledge_freshness: bool
    risk_threshold_met: bool
    contradictory_evidence: bool
    reasoning_quality: bool
    output_integrity: bool
    validated: bool
    validation_notes: list[str]
    validation_metadata: dict[str, object]
    created_at: datetime
    updated_at: datetime


class EvaluationMetricResponse(BaseModel):
    model_config = ConfigDict(extra="forbid", from_attributes=True, protected_namespaces=())

    id: UUID
    run_id: UUID | None
    metric_name: str
    metric_value: float
    benchmark_value: float | None
    target_value: float | None
    passed: bool
    metric_metadata: dict[str, object]
    created_at: datetime
    updated_at: datetime


class EvaluationRunResponse(BaseModel):
    model_config = ConfigDict(extra="forbid", from_attributes=True, protected_namespaces=())

    id: UUID
    trace_id: UUID | None
    dataset_name: str
    benchmark_name: str
    model_name: str
    status: str
    scorecard: dict[str, float]
    metrics: list[EvaluationMetricResponse]
    evaluation_metadata: dict[str, object]
    created_at: datetime
    updated_at: datetime


class ReasoningMetricsResponse(BaseModel):
    model_config = ConfigDict(extra="forbid", protected_namespaces=())

    total_traces: int
    total_decisions: int
    average_confidence: float
    average_trust: float
    average_risk: float
    hallucination_rate: float
    validation_pass_rate: float
    recommendation_success_rate: float
    reasoning_latency_ms: float
    confidence_distribution: dict[str, float]
    trust_distribution: dict[str, float]
    scorecard: dict[str, float]


class ReasoningAnalysisResponse(BaseModel):
    model_config = ConfigDict(extra="forbid", from_attributes=True, protected_namespaces=())

    id: UUID
    trace_id: UUID
    decision_id: UUID
    query: str
    strategy: str
    decision_summary: str
    decision_graph: list[dict[str, object]]
    reasoning_steps: list[str]
    evidence: list[EvidenceResponse]
    confidence: ConfidenceResponse
    trust: TrustResponse
    hallucination: HallucinationResponse
    validation: DecisionValidationResponse
    risk: RiskAssessmentResponse
    quantum_risk: QuantumRiskProjectionResponse
    recommendations: list[RecommendationResponse]
    source_references: list[str]
    knowledge_sources: list[str]
    mitre_references: list[str]
    compliance_references: list[str]
    risk_level: str
    business_impact: str
    technical_impact: str
    limitations: list[str]
    recommended_actions: list[str]
    alternative_actions: list[str]
    decision_metadata: dict[str, object]
    scorecard: dict[str, float]
    created_at: datetime
    updated_at: datetime
