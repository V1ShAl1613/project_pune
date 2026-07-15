from __future__ import annotations

from datetime import datetime

from sqlalchemy import DateTime, Float, Integer, JSON, String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import Uuid

from app.database.models.base import BaseModel, TimestampMixin, UUIDMixin


class Transaction(BaseModel, UUIDMixin, TimestampMixin):
    __tablename__ = "transactions"
    __table_args__ = (UniqueConstraint("transaction_id", name="uq_transactions_transaction_id"),)

    transaction_id: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    customer_id: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    account_id: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    merchant_id: Mapped[str | None] = mapped_column(String(255), nullable=True, index=True)
    beneficiary_id: Mapped[str | None] = mapped_column(String(255), nullable=True, index=True)
    amount: Mapped[float] = mapped_column(Float, nullable=False)
    currency: Mapped[str] = mapped_column(String(8), nullable=False, default="INR")
    transaction_type: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    channel: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    validation_status: Mapped[str] = mapped_column(String(32), nullable=False, default="validated")
    classification: Mapped[str] = mapped_column(String(64), nullable=False, default="normal")
    enrichment: Mapped[dict[str, object]] = mapped_column(JSON, nullable=False, default=dict)
    timeline: Mapped[list[dict[str, object]]] = mapped_column(JSON, nullable=False, default=list)
    transaction_metadata: Mapped[dict[str, object]] = mapped_column("metadata", JSON, nullable=False, default=dict)
    risk_score: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    fraud_score: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    aml_score: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)


class CustomerProfile(BaseModel, UUIDMixin, TimestampMixin):
    __tablename__ = "customer_profiles"
    __table_args__ = (UniqueConstraint("customer_id", name="uq_customer_profiles_customer_id"),)

    customer_id: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    customer_profile: Mapped[dict[str, object]] = mapped_column(JSON, nullable=False, default=dict)
    behavior_profile: Mapped[dict[str, object]] = mapped_column(JSON, nullable=False, default=dict)
    transaction_profile: Mapped[dict[str, object]] = mapped_column(JSON, nullable=False, default=dict)
    risk_history: Mapped[list[dict[str, object]]] = mapped_column(JSON, nullable=False, default=list)
    trust_score: Mapped[float] = mapped_column(Float, nullable=False, default=50.0)
    fraud_score: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    aml_score: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    compliance_score: Mapped[float] = mapped_column(Float, nullable=False, default=50.0)
    customer_timeline: Mapped[list[dict[str, object]]] = mapped_column(JSON, nullable=False, default=list)
    recommendations: Mapped[list[str]] = mapped_column(JSON, nullable=False, default=list)
    customer_metadata: Mapped[dict[str, object]] = mapped_column("metadata", JSON, nullable=False, default=dict)


class MerchantProfile(BaseModel, UUIDMixin, TimestampMixin):
    __tablename__ = "merchant_profiles"
    __table_args__ = (UniqueConstraint("merchant_id", name="uq_merchant_profiles_merchant_id"),)

    merchant_id: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    merchant_profile: Mapped[dict[str, object]] = mapped_column(JSON, nullable=False, default=dict)
    merchant_category: Mapped[str] = mapped_column(String(128), nullable=False, default="general")
    transaction_history: Mapped[list[dict[str, object]]] = mapped_column(JSON, nullable=False, default=list)
    chargeback_analysis: Mapped[dict[str, object]] = mapped_column(JSON, nullable=False, default=dict)
    settlement_analysis: Mapped[dict[str, object]] = mapped_column(JSON, nullable=False, default=dict)
    fraud_exposure: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    merchant_reputation: Mapped[float] = mapped_column(Float, nullable=False, default=50.0)
    merchant_risk: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    recommendations: Mapped[list[str]] = mapped_column(JSON, nullable=False, default=list)
    merchant_metadata: Mapped[dict[str, object]] = mapped_column("metadata", JSON, nullable=False, default=dict)


class BehaviorProfile(BaseModel, UUIDMixin, TimestampMixin):
    __tablename__ = "behavior_profiles"
    __table_args__ = (UniqueConstraint("entity_id", name="uq_behavior_profiles_entity_id"),)

    entity_id: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    entity_type: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    baseline_behavior: Mapped[dict[str, object]] = mapped_column(JSON, nullable=False, default=dict)
    behavior_deviation: Mapped[dict[str, object]] = mapped_column(JSON, nullable=False, default=dict)
    peer_comparison: Mapped[dict[str, object]] = mapped_column(JSON, nullable=False, default=dict)
    login_pattern: Mapped[dict[str, object]] = mapped_column(JSON, nullable=False, default=dict)
    transaction_pattern: Mapped[dict[str, object]] = mapped_column(JSON, nullable=False, default=dict)
    navigation_pattern: Mapped[dict[str, object]] = mapped_column(JSON, nullable=False, default=dict)
    device_pattern: Mapped[dict[str, object]] = mapped_column(JSON, nullable=False, default=dict)
    session_pattern: Mapped[dict[str, object]] = mapped_column(JSON, nullable=False, default=dict)
    risk_trend: Mapped[list[dict[str, object]]] = mapped_column(JSON, nullable=False, default=list)
    profile_metadata: Mapped[dict[str, object]] = mapped_column(JSON, nullable=False, default=dict)


class FraudCase(BaseModel, UUIDMixin, TimestampMixin):
    __tablename__ = "fraud_cases"
    __table_args__ = (UniqueConstraint("case_id", name="uq_fraud_cases_case_id"),)

    case_id: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    fraud_category: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    priority: Mapped[str] = mapped_column(String(32), nullable=False, default="high")
    status: Mapped[str] = mapped_column(String(32), nullable=False, default="open")
    customer_id: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    account_id: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    transaction_id: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    fraud_score: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    confidence: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    evidence: Mapped[list[dict[str, object]]] = mapped_column(JSON, nullable=False, default=list)
    transaction_timeline: Mapped[list[dict[str, object]]] = mapped_column(JSON, nullable=False, default=list)
    behavior_timeline: Mapped[list[dict[str, object]]] = mapped_column(JSON, nullable=False, default=list)
    linked_accounts: Mapped[list[str]] = mapped_column(JSON, nullable=False, default=list)
    linked_devices: Mapped[list[str]] = mapped_column(JSON, nullable=False, default=list)
    linked_merchants: Mapped[list[str]] = mapped_column(JSON, nullable=False, default=list)
    recommendations: Mapped[list[str]] = mapped_column(JSON, nullable=False, default=list)
    investigation_notes: Mapped[str] = mapped_column(Text, nullable=False, default="")
    analyst_actions: Mapped[list[str]] = mapped_column(JSON, nullable=False, default=list)
    business_impact: Mapped[str] = mapped_column(Text, nullable=False, default="")
    case_metadata: Mapped[dict[str, object]] = mapped_column("metadata", JSON, nullable=False, default=dict)


class AMLCase(BaseModel, UUIDMixin, TimestampMixin):
    __tablename__ = "aml_cases"
    __table_args__ = (UniqueConstraint("case_id", name="uq_aml_cases_case_id"),)

    case_id: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    customer_id: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    account_id: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    aml_score: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    cdd_status: Mapped[str] = mapped_column(String(32), nullable=False, default="complete")
    kyc_status: Mapped[str] = mapped_column(String(32), nullable=False, default="validated")
    pep_hits: Mapped[list[str]] = mapped_column(JSON, nullable=False, default=list)
    sanctions_hits: Mapped[list[str]] = mapped_column(JSON, nullable=False, default=list)
    watchlist_hits: Mapped[list[str]] = mapped_column(JSON, nullable=False, default=list)
    suspicious_patterns: Mapped[list[str]] = mapped_column(JSON, nullable=False, default=list)
    alerts: Mapped[list[str]] = mapped_column(JSON, nullable=False, default=list)
    case_status: Mapped[str] = mapped_column(String(32), nullable=False, default="open")
    recommendations: Mapped[list[str]] = mapped_column(JSON, nullable=False, default=list)
    business_impact: Mapped[str] = mapped_column(Text, nullable=False, default="")
    risk_factors: Mapped[list[str]] = mapped_column(JSON, nullable=False, default=list)
    case_metadata: Mapped[dict[str, object]] = mapped_column("metadata", JSON, nullable=False, default=dict)


class RiskScore(BaseModel, UUIDMixin, TimestampMixin):
    __tablename__ = "risk_scores"
    __table_args__ = (UniqueConstraint("entity_type", "entity_id", name="uq_risk_scores_entity"),)

    entity_type: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    entity_id: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    transaction_risk: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    customer_risk: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    merchant_risk: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    account_risk: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    identity_risk: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    behavior_risk: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    device_risk: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    aml_risk: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    overall_financial_risk: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    confidence: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    factors: Mapped[list[str]] = mapped_column(JSON, nullable=False, default=list)
    recommendations: Mapped[list[str]] = mapped_column(JSON, nullable=False, default=list)
    explainability: Mapped[dict[str, object]] = mapped_column(JSON, nullable=False, default=dict)


class DeviceProfile(BaseModel, UUIDMixin, TimestampMixin):
    __tablename__ = "device_profiles"
    __table_args__ = (UniqueConstraint("device_id", name="uq_device_profiles_device_id"),)

    device_id: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    device_fingerprint: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    browser: Mapped[str | None] = mapped_column(String(255), nullable=True)
    operating_system: Mapped[str | None] = mapped_column(String(255), nullable=True)
    ip_address: Mapped[str | None] = mapped_column(String(255), nullable=True, index=True)
    location: Mapped[str | None] = mapped_column(String(255), nullable=True)
    network: Mapped[str | None] = mapped_column(String(255), nullable=True)
    vpn_detected: Mapped[bool] = mapped_column(default=False)
    emulator_detected: Mapped[bool] = mapped_column(default=False)
    jailbreak_detected: Mapped[bool] = mapped_column(default=False)
    trusted_device: Mapped[bool] = mapped_column(default=False)
    device_reputation: Mapped[float] = mapped_column(Float, nullable=False, default=50.0)
    device_metadata: Mapped[dict[str, object]] = mapped_column("metadata", JSON, nullable=False, default=dict)


class IdentityProfile(BaseModel, UUIDMixin, TimestampMixin):
    __tablename__ = "identity_profiles"
    __table_args__ = (UniqueConstraint("identity_id", name="uq_identity_profiles_identity_id"),)

    identity_id: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    identity_type: Mapped[str] = mapped_column(String(64), nullable=False, default="customer")
    identity_risk: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    identity_metadata: Mapped[dict[str, object]] = mapped_column("metadata", JSON, nullable=False, default=dict)


class FinancialRecommendation(BaseModel, UUIDMixin, TimestampMixin):
    __tablename__ = "financial_recommendations"

    recommendation_type: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    action: Mapped[str] = mapped_column(Text, nullable=False)
    risk_domain: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    priority_rank: Mapped[int] = mapped_column(Integer, nullable=False, default=1)
    business_impact: Mapped[str] = mapped_column(Text, nullable=False, default="")
    technical_impact: Mapped[str] = mapped_column(Text, nullable=False, default="")
    recommendation_metadata: Mapped[dict[str, object]] = mapped_column("metadata", JSON, nullable=False, default=dict)


class BankingGraphNode(BaseModel, UUIDMixin, TimestampMixin):
    __tablename__ = "banking_graph_nodes"
    __table_args__ = (UniqueConstraint("node_key", name="uq_banking_graph_nodes_node_key"),)

    node_type: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    node_key: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    label: Mapped[str] = mapped_column(String(255), nullable=False)
    properties: Mapped[dict[str, object]] = mapped_column(JSON, nullable=False, default=dict)
    confidence: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)


class BankingGraphEdge(BaseModel, UUIDMixin, TimestampMixin):
    __tablename__ = "banking_graph_edges"

    source_node_key: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    target_node_key: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    relation_type: Mapped[str] = mapped_column(String(128), nullable=False, index=True)
    confidence: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    edge_metadata: Mapped[dict[str, object]] = mapped_column(JSON, nullable=False, default=dict)
