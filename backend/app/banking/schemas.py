from __future__ import annotations

from datetime import datetime
from enum import StrEnum
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, field_validator


class TransactionType(StrEnum):
    UPI = "upi"
    NEFT = "neft"
    RTGS = "rtgs"
    IMPS = "imps"
    CREDIT_CARD = "credit_card"
    DEBIT_CARD = "debit_card"
    ATM = "atm"
    POS = "pos"
    NET_BANKING = "net_banking"
    MOBILE_BANKING = "mobile_banking"
    WALLET = "wallet"
    SWIFT = "swift"
    INTERNATIONAL_TRANSFER = "international_transfer"
    STANDING_INSTRUCTION = "standing_instruction"
    RECURRING_PAYMENT = "recurring_payment"


class FraudCategory(StrEnum):
    ACCOUNT_TAKEOVER = "account_takeover"
    CARD_FRAUD = "card_fraud"
    IDENTITY_THEFT = "identity_theft"
    SYNTHETIC_IDENTITY = "synthetic_identity"
    MONEY_MULE = "money_mule"
    FRIENDLY_FRAUD = "friendly_fraud"
    MERCHANT_FRAUD = "merchant_fraud"
    LOAN_FRAUD = "loan_fraud"
    INSURANCE_FRAUD = "insurance_fraud"
    PAYMENT_FRAUD = "payment_fraud"
    WIRE_FRAUD = "wire_fraud"
    INTERNAL_FRAUD = "internal_fraud"


class CaseStatus(StrEnum):
    OPEN = "open"
    TRIAGED = "triaged"
    INVESTIGATING = "investigating"
    ESCALATED = "escalated"
    CLOSED = "closed"


class RiskEntityType(StrEnum):
    CUSTOMER = "customer"
    MERCHANT = "merchant"
    ACCOUNT = "account"
    DEVICE = "device"
    IDENTITY = "identity"
    TRANSACTION = "transaction"
    CHANNEL = "channel"


class BehaviorDimension(StrEnum):
    LOGIN_PATTERN = "login_pattern"
    TRANSACTION_PATTERN = "transaction_pattern"
    NAVIGATION_PATTERN = "navigation_pattern"
    DEVICE_PATTERN = "device_pattern"
    SESSION_PATTERN = "session_pattern"
    TIME_ANALYSIS = "time_analysis"
    PEER_COMPARISON = "peer_comparison"
    BASELINE_BEHAVIOR = "baseline_behavior"


class BankingTransactionRequest(BaseModel):
    model_config = ConfigDict(extra="forbid", protected_namespaces=())

    transaction_id: str = Field(min_length=1, max_length=255)
    customer_id: str = Field(min_length=1, max_length=255)
    account_id: str = Field(min_length=1, max_length=255)
    merchant_id: str | None = None
    beneficiary_id: str | None = None
    amount: float = Field(gt=0)
    currency: str = Field(default="INR", min_length=3, max_length=8)
    transaction_type: TransactionType = TransactionType.UPI
    channel: str = Field(default="mobile", min_length=1, max_length=64)
    timestamp: datetime | None = None
    device_id: str | None = None
    ip_address: str | None = None
    location: str | None = None
    description: str | None = None
    metadata: dict[str, object] = Field(default_factory=dict)
    history: list[dict[str, object]] = Field(default_factory=list)

    @field_validator("currency", "channel")
    @classmethod
    def _normalize(cls, value: str) -> str:
        return value.strip()


class FraudAnalyzeRequest(BankingTransactionRequest):
    fraud_category_hint: FraudCategory | None = None
    peer_history: list[dict[str, object]] = Field(default_factory=list)
    device_history: list[dict[str, object]] = Field(default_factory=list)
    merchant_history: list[dict[str, object]] = Field(default_factory=list)
    linked_accounts: list[str] = Field(default_factory=list)
    linked_devices: list[str] = Field(default_factory=list)
    linked_merchants: list[str] = Field(default_factory=list)
    linked_channels: list[str] = Field(default_factory=list)
    aml_flags: list[str] = Field(default_factory=list)


class FraudScoreRequest(BaseModel):
    model_config = ConfigDict(extra="forbid", protected_namespaces=())

    transaction_id: str
    customer_id: str
    account_id: str
    amount: float = Field(gt=0)
    currency: str = "INR"
    transaction_type: TransactionType = TransactionType.UPI
    channel: str = "mobile"
    merchant_id: str | None = None
    device_id: str | None = None
    ip_address: str | None = None
    location: str | None = None
    metadata: dict[str, object] = Field(default_factory=dict)
    history: list[dict[str, object]] = Field(default_factory=list)


class FraudInvestigateRequest(FraudAnalyzeRequest):
    case_id: str | None = None
    analyst_notes: str | None = None
    analyst_actions: list[str] = Field(default_factory=list)
    evidence: list[dict[str, object]] = Field(default_factory=list)


class AMLAnalyzeRequest(BaseModel):
    model_config = ConfigDict(extra="forbid", protected_namespaces=())

    customer_id: str
    account_id: str
    customer_name: str | None = None
    kyc_validated: bool = True
    cdd_complete: bool = True
    edd_required: bool = False
    pep_matches: list[str] = Field(default_factory=list)
    sanctions_matches: list[str] = Field(default_factory=list)
    watchlist_matches: list[str] = Field(default_factory=list)
    cash_transactions: int = Field(default=0, ge=0)
    large_cash_amount: float = Field(default=0.0, ge=0.0)
    suspicious_transactions: list[dict[str, object]] = Field(default_factory=list)
    counterparties: list[str] = Field(default_factory=list)
    countries: list[str] = Field(default_factory=list)
    metadata: dict[str, object] = Field(default_factory=dict)


class UEBAAnalyzeRequest(BaseModel):
    model_config = ConfigDict(extra="forbid", protected_namespaces=())

    entity_id: str
    entity_type: RiskEntityType = RiskEntityType.CUSTOMER
    login_history: list[dict[str, object]] = Field(default_factory=list)
    transaction_history: list[dict[str, object]] = Field(default_factory=list)
    navigation_history: list[dict[str, object]] = Field(default_factory=list)
    device_history: list[dict[str, object]] = Field(default_factory=list)
    session_history: list[dict[str, object]] = Field(default_factory=list)
    peer_history: list[dict[str, object]] = Field(default_factory=list)
    metadata: dict[str, object] = Field(default_factory=dict)


class FraudCaseCreateRequest(FraudInvestigateRequest):
    priority: str = Field(default="high", min_length=1, max_length=32)


class CustomerRiskLookupRequest(BaseModel):
    customer_id: str


class MerchantRiskLookupRequest(BaseModel):
    merchant_id: str


class AccountRiskLookupRequest(BaseModel):
    account_id: str


class TransactionResponse(BaseModel):
    model_config = ConfigDict(extra="forbid", from_attributes=True, protected_namespaces=())

    id: UUID
    transaction_id: str
    customer_id: str
    account_id: str
    merchant_id: str | None
    beneficiary_id: str | None
    amount: float
    currency: str
    transaction_type: str
    channel: str
    validation_status: str
    classification: str
    enrichment: dict[str, object]
    timeline: list[dict[str, object]]
    metadata: dict[str, object]
    risk_score: float
    fraud_score: float
    aml_score: float
    created_at: datetime
    updated_at: datetime


class FraudAnalysisResponse(BaseModel):
    model_config = ConfigDict(extra="forbid", from_attributes=True, protected_namespaces=())

    id: UUID
    transaction_id: str
    customer_id: str
    account_id: str
    fraud_category: str
    fraud_score: float
    confidence: float
    evidence: list[dict[str, object]]
    behavior_indicators: list[str]
    velocity_indicators: list[str]
    anomaly_indicators: list[str]
    location_indicators: list[str]
    merchant_indicators: list[str]
    account_indicators: list[str]
    linked_transactions: list[str]
    risk_factors: list[str]
    recommendations: list[str]
    business_impact: str
    explainability: dict[str, object]
    metadata: dict[str, object]
    created_at: datetime
    updated_at: datetime


class FraudScoreResponse(BaseModel):
    model_config = ConfigDict(extra="forbid", protected_namespaces=())

    transaction_id: str
    fraud_score: float
    risk_level: str
    confidence: float
    factors: list[str]
    metadata: dict[str, object]


class FraudCaseResponse(BaseModel):
    model_config = ConfigDict(extra="forbid", from_attributes=True, protected_namespaces=())

    id: UUID
    case_id: str
    fraud_category: str
    priority: str
    status: str
    customer_id: str
    account_id: str
    transaction_id: str
    evidence: list[dict[str, object]]
    transaction_timeline: list[dict[str, object]]
    behavior_timeline: list[dict[str, object]]
    linked_accounts: list[str]
    linked_devices: list[str]
    linked_merchants: list[str]
    recommendations: list[str]
    investigation_notes: str
    analyst_actions: list[str]
    business_impact: str
    metadata: dict[str, object]
    created_at: datetime
    updated_at: datetime


class AMLAnalysisResponse(BaseModel):
    model_config = ConfigDict(extra="forbid", from_attributes=True, protected_namespaces=())

    id: UUID
    customer_id: str
    account_id: str
    aml_score: float
    cdd_status: str
    kyc_status: str
    pep_hits: list[str]
    sanctions_hits: list[str]
    watchlist_hits: list[str]
    suspicious_patterns: list[str]
    alerts: list[str]
    case_status: str
    recommendations: list[str]
    business_impact: str
    risk_factors: list[str]
    metadata: dict[str, object]
    created_at: datetime
    updated_at: datetime


class UEBAAnalysisResponse(BaseModel):
    model_config = ConfigDict(extra="forbid", from_attributes=True, protected_namespaces=())

    id: UUID
    entity_id: str
    entity_type: str
    baseline_behavior: dict[str, object]
    behavior_deviation: dict[str, object]
    peer_comparison: dict[str, object]
    login_pattern: dict[str, object]
    transaction_pattern: dict[str, object]
    navigation_pattern: dict[str, object]
    device_pattern: dict[str, object]
    session_pattern: dict[str, object]
    risk_trend: list[dict[str, object]]
    indicators: list[str]
    confidence: float
    recommendations: list[str]
    metadata: dict[str, object]
    created_at: datetime
    updated_at: datetime


class RiskScoreResponse(BaseModel):
    model_config = ConfigDict(extra="forbid", from_attributes=True, protected_namespaces=())

    id: UUID
    entity_type: str
    entity_id: str
    transaction_risk: float
    customer_risk: float
    merchant_risk: float
    account_risk: float
    identity_risk: float
    behavior_risk: float
    device_risk: float
    aml_risk: float
    overall_financial_risk: float
    confidence: float
    factors: list[str]
    recommendations: list[str]
    explainability: dict[str, object]
    created_at: datetime
    updated_at: datetime


class CustomerRiskResponse(BaseModel):
    model_config = ConfigDict(extra="forbid", from_attributes=True, protected_namespaces=())

    id: UUID
    customer_id: str
    customer_profile: dict[str, object]
    behavior_profile: dict[str, object]
    transaction_profile: dict[str, object]
    risk_history: list[dict[str, object]]
    trust_score: float
    fraud_score: float
    aml_score: float
    compliance_score: float
    recommendations: list[str]
    customer_timeline: list[dict[str, object]]
    metadata: dict[str, object]
    created_at: datetime
    updated_at: datetime


class MerchantRiskResponse(BaseModel):
    model_config = ConfigDict(extra="forbid", from_attributes=True, protected_namespaces=())

    id: UUID
    merchant_id: str
    merchant_profile: dict[str, object]
    merchant_category: str
    transaction_history: list[dict[str, object]]
    chargeback_analysis: dict[str, object]
    settlement_analysis: dict[str, object]
    fraud_exposure: float
    merchant_reputation: float
    merchant_risk: float
    recommendations: list[str]
    metadata: dict[str, object]
    created_at: datetime
    updated_at: datetime


class AccountRiskResponse(BaseModel):
    model_config = ConfigDict(extra="forbid", from_attributes=True, protected_namespaces=())

    id: UUID
    account_id: str
    account_risk: float
    identity_risk: float
    behavior_risk: float
    device_risk: float
    transaction_risk: float
    recommendations: list[str]
    metadata: dict[str, object]
    created_at: datetime
    updated_at: datetime


class FinancialRecommendationResponse(BaseModel):
    model_config = ConfigDict(extra="forbid", from_attributes=True, protected_namespaces=())

    id: UUID
    recommendation_type: str
    title: str
    action: str
    risk_domain: str
    priority_rank: int
    business_impact: str
    technical_impact: str
    metadata: dict[str, object]
    created_at: datetime
    updated_at: datetime


class InvestigationNoteResponse(BaseModel):
    model_config = ConfigDict(extra="forbid", from_attributes=True, protected_namespaces=())

    note: str
    analyst_actions: list[str]
    created_at: datetime


class RiskDashboardResponse(BaseModel):
    model_config = ConfigDict(extra="forbid", protected_namespaces=())

    transactions_per_second: float
    fraud_detection_rate: float
    aml_alerts: int
    ueba_events: int
    false_positives: int
    false_negatives: int
    risk_distribution: dict[str, float]
    investigation_time_minutes: float
    fraud_trends: list[dict[str, object]]
    scorecard: dict[str, float]


class TransactionSearchRequest(BaseModel):
    query: str
    limit: int = Field(default=25, ge=1, le=200)


class TransactionSearchResponse(BaseModel):
    model_config = ConfigDict(extra="forbid", protected_namespaces=())

    query: str
    matches: list[dict[str, object]]
    count: int
