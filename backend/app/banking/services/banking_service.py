from __future__ import annotations

import json
import logging
from dataclasses import dataclass, field
from datetime import UTC, datetime
from hashlib import sha256
from uuid import uuid4

from redis.asyncio import Redis

from app.banking.models import AMLCase, BankingGraphEdge, BankingGraphNode, BehaviorProfile, CustomerProfile, DeviceProfile, FinancialRecommendation, FraudCase, IdentityProfile, MerchantProfile, RiskScore, Transaction
from app.banking.repositories.banking_repository import BankingRepository
from app.banking.schemas import (
    AMLAnalyzeRequest,
    AMLAnalysisResponse,
    AccountRiskLookupRequest,
    AccountRiskResponse,
    BankingTransactionRequest,
    BehaviorDimension,
    CaseStatus,
    CustomerRiskLookupRequest,
    CustomerRiskResponse,
    FraudAnalyzeRequest,
    FraudAnalysisResponse,
    FraudCaseCreateRequest,
    FraudCaseResponse,
    FraudInvestigateRequest,
    FraudScoreRequest,
    FraudScoreResponse,
    FinancialRecommendationResponse,
    MerchantRiskLookupRequest,
    MerchantRiskResponse,
    RiskDashboardResponse,
    RiskScoreResponse,
    RiskEntityType,
    TransactionResponse,
    TransactionSearchRequest,
    TransactionSearchResponse,
    TransactionType,
    UEBAAnalyzeRequest,
    UEBAAnalysisResponse,
)
from app.banking.shared import BankingGraphBackend, BankingIntelligenceEngine, build_graph_backend, _clamp, _now, _normalize
from app.core.settings import AppSettings
from app.knowledge.vectorstore.qdrant_store import QdrantVectorStore, VectorPoint


@dataclass(slots=True)
class BankingService:
    repository: BankingRepository | None
    settings: AppSettings
    redis_client: Redis | None
    logger: logging.Logger
    engine: BankingIntelligenceEngine = field(init=False)
    graph_backend: BankingGraphBackend = field(init=False)
    vector_store: QdrantVectorStore = field(init=False)

    def __post_init__(self) -> None:
        self.repository = self.repository or BankingRepository()
        self.engine = BankingIntelligenceEngine()
        self.graph_backend = BankingGraphBackend()
        self.vector_store = QdrantVectorStore(self.settings)

    async def analyze_transaction(self, request: BankingTransactionRequest) -> TransactionResponse:
        cached = await self._cache_get(self._cache_key("transaction", request))
        if cached:
            return TransactionResponse.model_validate(cached)
        history = request.history
        bundle = self.engine.classify_transaction(request, history)
        transaction = Transaction(transaction_id=request.transaction_id, customer_id=request.customer_id, account_id=request.account_id, merchant_id=request.merchant_id, beneficiary_id=request.beneficiary_id, amount=request.amount, currency=request.currency, transaction_type=request.transaction_type.value, channel=request.channel, validation_status=bundle["validation_status"], classification=bundle["classification"], enrichment=bundle["enrichment"], timeline=self._transaction_timeline(request, history), transaction_metadata=request.metadata, risk_score=bundle["risk_score"], fraud_score=bundle["fraud_score"], aml_score=bundle["aml_score"])
        await self.repository.add_transaction(transaction)
        self._graph_transaction(request, transaction)
        response = self._transaction_response(transaction)
        await self._cache_set(self._cache_key("transaction", request), response.model_dump(mode="json"), self.settings.banking_cache_ttl_seconds)
        return response

    async def analyze_fraud(self, request: FraudAnalyzeRequest) -> FraudAnalysisResponse:
        cached = await self._cache_get(self._cache_key("fraud", request))
        if cached:
            return FraudAnalysisResponse.model_validate(cached)
        transaction = await self.analyze_transaction(request)
        profile = await self._customer_profile_bundle(request.customer_id)
        behavior = await self._behavior_bundle(request.customer_id, request)
        device = await self._device_bundle(request)
        bundle = self.engine.fraud_analysis(request, profile, behavior, device)
        fraud_case = FraudCase(case_id=f"fraud-{request.transaction_id}", fraud_category=bundle["fraud_category"], priority="high" if bundle["fraud_score"] >= 70 else "medium", status=CaseStatus.OPEN.value, customer_id=request.customer_id, account_id=request.account_id, transaction_id=request.transaction_id, fraud_score=bundle["fraud_score"], confidence=bundle["confidence"], evidence=bundle["evidence"], transaction_timeline=transaction.timeline, behavior_timeline=behavior["risk_trend"], linked_accounts=request.linked_accounts, linked_devices=request.linked_devices, linked_merchants=request.linked_merchants, recommendations=bundle["recommendations"], investigation_notes=request.description or "", analyst_actions=[], business_impact=bundle["business_impact"], case_metadata={**request.metadata, **bundle["explainability"]})
        await self.repository.add_fraud_case(fraud_case)
        await self._store_recommendations(bundle["recommendations"], "fraud", request.transaction_id, fraud_case.fraud_category)
        response = FraudAnalysisResponse(id=fraud_case.id or uuid4(), transaction_id=fraud_case.transaction_id, customer_id=fraud_case.customer_id, account_id=fraud_case.account_id, fraud_category=fraud_case.fraud_category, fraud_score=fraud_case.fraud_score, confidence=fraud_case.confidence, evidence=fraud_case.evidence, behavior_indicators=bundle["behavior_indicators"], velocity_indicators=bundle["velocity_indicators"], anomaly_indicators=bundle["anomaly_indicators"], location_indicators=bundle["location_indicators"], merchant_indicators=bundle["merchant_indicators"], account_indicators=bundle["account_indicators"], linked_transactions=bundle["linked_transactions"], risk_factors=bundle["risk_factors"], recommendations=bundle["recommendations"], business_impact=bundle["business_impact"], explainability=bundle["explainability"], metadata=request.metadata, created_at=fraud_case.created_at or datetime.now(UTC), updated_at=fraud_case.updated_at or datetime.now(UTC))
        await self._cache_set(self._cache_key("fraud", request), response.model_dump(mode="json"), self.settings.banking_cache_ttl_seconds)
        return response

    async def score_fraud(self, request: FraudScoreRequest) -> FraudScoreResponse:
        analysis = await self.analyze_fraud(FraudAnalyzeRequest(**request.model_dump()))
        risk_level = self._risk_level(analysis.fraud_score)
        return FraudScoreResponse(transaction_id=request.transaction_id, fraud_score=analysis.fraud_score, risk_level=risk_level, confidence=analysis.confidence, factors=analysis.risk_factors, metadata=request.metadata)

    async def investigate_fraud(self, request: FraudInvestigateRequest) -> FraudCaseResponse:
        analysis = await self.analyze_fraud(request)
        history = request.history
        bundle = self.engine.investigation(request, analysis.model_dump(mode="json"), history)
        fraud_case = FraudCase(case_id=bundle["case_id"], fraud_category=bundle["fraud_category"], priority=bundle["priority"], status=bundle["status"], customer_id=request.customer_id, account_id=request.account_id, transaction_id=request.transaction_id, fraud_score=analysis.fraud_score, confidence=analysis.confidence, evidence=bundle["evidence"], transaction_timeline=bundle["transaction_timeline"], behavior_timeline=bundle["behavior_timeline"], linked_accounts=bundle["linked_accounts"], linked_devices=bundle["linked_devices"], linked_merchants=bundle["linked_merchants"], recommendations=bundle["recommendations"], investigation_notes=bundle["investigation_notes"], analyst_actions=bundle["analyst_actions"], business_impact=bundle["business_impact"], case_metadata=bundle["metadata"])
        await self.repository.add_fraud_case(fraud_case)
        return FraudCaseResponse(id=fraud_case.id or uuid4(), case_id=fraud_case.case_id, fraud_category=fraud_case.fraud_category, priority=fraud_case.priority, status=fraud_case.status, customer_id=fraud_case.customer_id, account_id=fraud_case.account_id, transaction_id=fraud_case.transaction_id, evidence=fraud_case.evidence, transaction_timeline=fraud_case.transaction_timeline, behavior_timeline=fraud_case.behavior_timeline, linked_accounts=fraud_case.linked_accounts, linked_devices=fraud_case.linked_devices, linked_merchants=fraud_case.linked_merchants, recommendations=fraud_case.recommendations, investigation_notes=fraud_case.investigation_notes, analyst_actions=fraud_case.analyst_actions, business_impact=fraud_case.business_impact, metadata=fraud_case.case_metadata, created_at=fraud_case.created_at or datetime.now(UTC), updated_at=fraud_case.updated_at or datetime.now(UTC))

    async def analyze_aml(self, request: AMLAnalyzeRequest) -> AMLAnalysisResponse:
        cached = await self._cache_get(self._cache_key("aml", request))
        if cached:
            return AMLAnalysisResponse.model_validate(cached)
        bundle = self.engine.aml_analysis(request)
        aml_case = AMLCase(case_id=f"aml-{request.customer_id}", customer_id=request.customer_id, account_id=request.account_id, aml_score=bundle["aml_score"], cdd_status=bundle["cdd_status"], kyc_status=bundle["kyc_status"], pep_hits=bundle["pep_hits"], sanctions_hits=bundle["sanctions_hits"], watchlist_hits=bundle["watchlist_hits"], suspicious_patterns=bundle["suspicious_patterns"], alerts=bundle["alerts"], case_status=bundle["case_status"], recommendations=bundle["recommendations"], business_impact=bundle["business_impact"], risk_factors=bundle["risk_factors"], case_metadata=bundle["metadata"])
        await self.repository.add_aml_case(aml_case)
        await self._store_recommendations(bundle["recommendations"], "aml", request.customer_id, aml_case.case_id)
        response = AMLAnalysisResponse(id=aml_case.id or uuid4(), customer_id=aml_case.customer_id, account_id=aml_case.account_id, aml_score=aml_case.aml_score, cdd_status=aml_case.cdd_status, kyc_status=aml_case.kyc_status, pep_hits=aml_case.pep_hits, sanctions_hits=aml_case.sanctions_hits, watchlist_hits=aml_case.watchlist_hits, suspicious_patterns=aml_case.suspicious_patterns, alerts=aml_case.alerts, case_status=aml_case.case_status, recommendations=aml_case.recommendations, business_impact=aml_case.business_impact, risk_factors=aml_case.risk_factors, metadata=request.metadata, created_at=aml_case.created_at or datetime.now(UTC), updated_at=aml_case.updated_at or datetime.now(UTC))
        await self._cache_set(self._cache_key("aml", request), response.model_dump(mode="json"), self.settings.banking_cache_ttl_seconds)
        return response

    async def analyze_ueba(self, request: UEBAAnalyzeRequest) -> UEBAAnalysisResponse:
        cached = await self._cache_get(self._cache_key("ueba", request))
        if cached:
            return UEBAAnalysisResponse.model_validate(cached)
        bundle = self.engine.ueba_analysis(request)
        behavior_profile = BehaviorProfile(entity_id=request.entity_id, entity_type=request.entity_type.value, baseline_behavior=bundle["baseline_behavior"], behavior_deviation=bundle["behavior_deviation"], peer_comparison=bundle["peer_comparison"], login_pattern=bundle["login_pattern"], transaction_pattern=bundle["transaction_pattern"], navigation_pattern=bundle["navigation_pattern"], device_pattern=bundle["device_pattern"], session_pattern=bundle["session_pattern"], risk_trend=bundle["risk_trend"], profile_metadata=request.metadata)
        await self.repository.add_behavior_profile(behavior_profile)
        response = UEBAAnalysisResponse(id=behavior_profile.id or uuid4(), entity_id=behavior_profile.entity_id, entity_type=behavior_profile.entity_type, baseline_behavior=behavior_profile.baseline_behavior, behavior_deviation=behavior_profile.behavior_deviation, peer_comparison=behavior_profile.peer_comparison, login_pattern=behavior_profile.login_pattern, transaction_pattern=behavior_profile.transaction_pattern, navigation_pattern=behavior_profile.navigation_pattern, device_pattern=behavior_profile.device_pattern, session_pattern=behavior_profile.session_pattern, risk_trend=behavior_profile.risk_trend, indicators=bundle["indicators"], confidence=bundle["confidence"], recommendations=bundle["recommendations"], metadata=request.metadata, created_at=behavior_profile.created_at or datetime.now(UTC), updated_at=behavior_profile.updated_at or datetime.now(UTC))
        await self._cache_set(self._cache_key("ueba", request), response.model_dump(mode="json"), self.settings.banking_cache_ttl_seconds)
        return response

    async def customer_risk(self, request: CustomerRiskLookupRequest) -> CustomerRiskResponse:
        bundle = await self._customer_profile_bundle(request.customer_id)
        profile = CustomerProfile(customer_id=request.customer_id, customer_profile=bundle["customer_profile"], behavior_profile=bundle["behavior_profile"], transaction_profile=bundle["transaction_profile"], risk_history=bundle["risk_history"], trust_score=bundle["trust_score"], fraud_score=bundle["fraud_score"], aml_score=bundle["aml_score"], compliance_score=bundle["compliance_score"], customer_timeline=bundle["customer_timeline"], recommendations=bundle["recommendations"], customer_metadata=bundle["metadata"])
        await self.repository.add_customer_profile(profile)
        return CustomerRiskResponse(id=profile.id or uuid4(), customer_id=profile.customer_id, customer_profile=profile.customer_profile, behavior_profile=profile.behavior_profile, transaction_profile=profile.transaction_profile, risk_history=profile.risk_history, trust_score=profile.trust_score, fraud_score=profile.fraud_score, aml_score=profile.aml_score, compliance_score=profile.compliance_score, recommendations=profile.recommendations, customer_timeline=profile.customer_timeline, metadata=profile.customer_metadata, created_at=profile.created_at or datetime.now(UTC), updated_at=profile.updated_at or datetime.now(UTC))

    async def merchant_risk(self, request: MerchantRiskLookupRequest) -> MerchantRiskResponse:
        transactions = [self._transaction_payload(item) for item in await self.repository.list_transactions() if item.merchant_id == request.merchant_id]
        bundle = self.engine.merchant_profile(request.merchant_id, transactions)
        profile = MerchantProfile(merchant_id=request.merchant_id, merchant_profile=bundle["merchant_profile"], merchant_category=bundle["merchant_category"], transaction_history=bundle["transaction_history"], chargeback_analysis=bundle["chargeback_analysis"], settlement_analysis=bundle["settlement_analysis"], fraud_exposure=bundle["fraud_exposure"], merchant_reputation=bundle["merchant_reputation"], merchant_risk=bundle["merchant_risk"], recommendations=bundle["recommendations"], merchant_metadata=bundle["metadata"])
        await self.repository.add_merchant_profile(profile)
        return MerchantRiskResponse(id=profile.id or uuid4(), merchant_id=profile.merchant_id, merchant_profile=profile.merchant_profile, merchant_category=profile.merchant_category, transaction_history=profile.transaction_history, chargeback_analysis=profile.chargeback_analysis, settlement_analysis=profile.settlement_analysis, fraud_exposure=profile.fraud_exposure, merchant_reputation=profile.merchant_reputation, merchant_risk=profile.merchant_risk, recommendations=profile.recommendations, metadata=profile.merchant_metadata, created_at=profile.created_at or datetime.now(UTC), updated_at=profile.updated_at or datetime.now(UTC))

    async def account_risk(self, request: AccountRiskLookupRequest) -> AccountRiskResponse:
        transactions = [item for item in await self.repository.list_transactions() if item.account_id == request.account_id]
        transaction_risk = _clamp(mean([item.fraud_score for item in transactions]) if transactions else 35.0)
        behavior_risk = _clamp(mean([profile.behavior_deviation.get("score", 40.0) for profile in await self.repository.list_behaviors() if profile.entity_id == request.account_id]) if await self.repository.list_behaviors() else 40.0)
        device_risk = _clamp(mean([device.device_reputation for device in await self.repository.list_devices()]) if await self.repository.list_devices() else 45.0)
        identity_risk = _clamp(mean([identity.identity_risk for identity in await self.repository.list_identities()]) if await self.repository.list_identities() else 40.0)
        bundle = self.engine.account_risk(request.account_id, transaction_risk, behavior_risk, device_risk, identity_risk)
        return AccountRiskResponse(id=uuid4(), account_id=request.account_id, account_risk=bundle["account_risk"], identity_risk=bundle["identity_risk"], behavior_risk=bundle["behavior_risk"], device_risk=bundle["device_risk"], transaction_risk=bundle["transaction_risk"], recommendations=bundle["recommendations"], metadata=bundle["metadata"], created_at=datetime.now(UTC), updated_at=datetime.now(UTC))

    async def risk_dashboard(self) -> RiskDashboardResponse:
        dashboard = self.engine.dashboard(await self.repository.list_transactions(), await self.repository.list_fraud_cases(), await self.repository.list_aml_cases(), await self.repository.list_behaviors(), await self.repository.list_risk_scores())
        return RiskDashboardResponse.model_validate(dashboard)

    async def fraud_cases(self) -> list[FraudCaseResponse]:
        return [self._fraud_case_response(case) for case in await self.repository.list_fraud_cases()]

    async def transaction_search(self, request: TransactionSearchRequest) -> TransactionSearchResponse:
        query = request.query.lower()
        matches = [self._transaction_payload(transaction) for transaction in await self.repository.list_transactions() if query in transaction.transaction_id.lower() or query in transaction.customer_id.lower() or query in transaction.account_id.lower() or query in (transaction.merchant_id or "").lower()]
        return TransactionSearchResponse(query=request.query, matches=matches[: request.limit], count=len(matches))

    async def financial_recommendations(self) -> list[FinancialRecommendationResponse]:
        return [self._recommendation_response(recommendation) for recommendation in await self.repository.list_recommendations()]

    async def _customer_profile_bundle(self, customer_id: str) -> dict[str, object]:
        transactions = [self._transaction_payload(item) for item in await self.repository.list_transactions() if item.customer_id == customer_id]
        behavior_history = [self._behavior_payload(item) for item in await self.repository.list_behaviors() if item.entity_id == customer_id]
        risk_history = [self._risk_score_payload(score) for score in await self.repository.list_risk_scores() if score.entity_id == customer_id]
        return self.engine.customer_profile(customer_id, risk_history, transactions, behavior_history)

    async def _behavior_bundle(self, customer_id: str, request: FraudAnalyzeRequest) -> dict[str, object]:
        request = UEBAAnalyzeRequest(entity_id=customer_id, entity_type=RiskEntityType.CUSTOMER, login_history=request.history, transaction_history=request.history, navigation_history=[], device_history=request.device_history, session_history=[], peer_history=request.peer_history, metadata=request.metadata)
        return self.engine.ueba_analysis(request)

    async def _device_bundle(self, request: FraudAnalyzeRequest) -> dict[str, object]:
        fingerprint = self._device_fingerprint(request)
        profile = DeviceProfile(device_id=request.device_id or fingerprint, device_fingerprint=fingerprint, browser=str(request.metadata.get("browser", "unknown")), operating_system=str(request.metadata.get("os", "unknown")), ip_address=request.ip_address, location=request.location, network=str(request.metadata.get("network", "unknown")), vpn_detected=bool(request.metadata.get("vpn_detected", False)), emulator_detected=bool(request.metadata.get("emulator_detected", False)), jailbreak_detected=bool(request.metadata.get("jailbreak_detected", False)), trusted_device=bool(request.metadata.get("trusted_device", False)), device_reputation=_clamp(75.0 - (12.0 if request.device_id else 0.0) - (8.0 if request.ip_address else 0.0)), device_metadata=request.metadata)
        await self.repository.add_device_profile(profile)
        return {"device_reputation": profile.device_reputation, "location": profile.location, "ip_address": profile.ip_address, "metadata": profile.device_metadata}

    async def _store_recommendations(self, recommendations: list[str], recommendation_type: str, entity_id: str, risk_domain: str) -> None:
        for index, recommendation in enumerate(recommendations, start=1):
            await self.repository.add_recommendation(FinancialRecommendation(recommendation_type=recommendation_type, title=f"{recommendation_type.title()} Recommendation {index}", action=recommendation, risk_domain=risk_domain, priority_rank=index, business_impact="Financial exposure reduced through intervention.", technical_impact="Banking intelligence controls updated.", recommendation_metadata={"entity_id": entity_id, "priority_rank": index}))

    def _graph_transaction(self, request: BankingTransactionRequest, transaction: Transaction) -> None:
        nodes, edges = self.engine.graph_seed(request, self._transaction_payload(transaction))
        for node in nodes:
            self.graph_backend.add_node(node["node_key"], node["node_type"], node["label"], **dict(node.get("properties") or {}))
            self.repository.graph_nodes.append(BankingGraphNode(node_type=str(node["node_type"]), node_key=str(node["node_key"]), label=str(node["label"]), properties=dict(node.get("properties") or {}), confidence=90.0))
        for edge in edges:
            self.graph_backend.add_edge(edge["source"], edge["target"], edge["relation_type"], float(edge.get("confidence", 50.0)), **dict(edge.get("metadata") or {}))
            self.repository.graph_edges.append(BankingGraphEdge(source_node_key=str(edge["source"]), target_node_key=str(edge["target"]), relation_type=str(edge["relation_type"]), confidence=float(edge.get("confidence", 50.0)), edge_metadata=dict(edge.get("metadata") or {})))

    def _transaction_payload(self, transaction: Transaction) -> dict[str, object]:
        return {
            "id": str(transaction.id) if transaction.id else None,
            "transaction_id": transaction.transaction_id,
            "customer_id": transaction.customer_id,
            "account_id": transaction.account_id,
            "merchant_id": transaction.merchant_id,
            "beneficiary_id": transaction.beneficiary_id,
            "amount": transaction.amount,
            "currency": transaction.currency,
            "transaction_type": transaction.transaction_type,
            "channel": transaction.channel,
            "validation_status": transaction.validation_status,
            "classification": transaction.classification,
            "enrichment": transaction.enrichment,
            "timeline": transaction.timeline,
            "metadata": transaction.transaction_metadata,
            "risk_score": transaction.risk_score,
            "fraud_score": transaction.fraud_score,
            "aml_score": transaction.aml_score,
        }

    def _transaction_timeline(self, request: BankingTransactionRequest, history: list[dict[str, object]]) -> list[dict[str, object]]:
        now = request.timestamp or _now()
        timeline = [{"timestamp": now, "event": "transaction_initiated", "transaction_id": request.transaction_id, "amount": request.amount}]
        for index, item in enumerate(history[:5], start=1):
            timeline.append({"timestamp": now, "event": item.get("event", item.get("transaction_id", f"history-{index}")), "risk": float(item.get("risk", item.get("risk_score", 0.0)))})
        return timeline

    def _transaction_response(self, transaction: Transaction) -> TransactionResponse:
        return TransactionResponse(id=transaction.id or uuid4(), transaction_id=transaction.transaction_id, customer_id=transaction.customer_id, account_id=transaction.account_id, merchant_id=transaction.merchant_id, beneficiary_id=transaction.beneficiary_id, amount=transaction.amount, currency=transaction.currency, transaction_type=transaction.transaction_type, channel=transaction.channel, validation_status=transaction.validation_status, classification=transaction.classification, enrichment=transaction.enrichment, timeline=transaction.timeline, metadata=transaction.transaction_metadata, risk_score=transaction.risk_score, fraud_score=transaction.fraud_score, aml_score=transaction.aml_score, created_at=transaction.created_at or datetime.now(UTC), updated_at=transaction.updated_at or datetime.now(UTC))

    def _fraud_case_response(self, fraud_case: FraudCase) -> FraudCaseResponse:
        return FraudCaseResponse(id=fraud_case.id or uuid4(), case_id=fraud_case.case_id, fraud_category=fraud_case.fraud_category, priority=fraud_case.priority, status=fraud_case.status, customer_id=fraud_case.customer_id, account_id=fraud_case.account_id, transaction_id=fraud_case.transaction_id, evidence=fraud_case.evidence, transaction_timeline=fraud_case.transaction_timeline, behavior_timeline=fraud_case.behavior_timeline, linked_accounts=fraud_case.linked_accounts, linked_devices=fraud_case.linked_devices, linked_merchants=fraud_case.linked_merchants, recommendations=fraud_case.recommendations, investigation_notes=fraud_case.investigation_notes, analyst_actions=fraud_case.analyst_actions, business_impact=fraud_case.business_impact, metadata=fraud_case.case_metadata, created_at=fraud_case.created_at or datetime.now(UTC), updated_at=fraud_case.updated_at or datetime.now(UTC))

    def _recommendation_response(self, recommendation: FinancialRecommendation) -> FinancialRecommendationResponse:
        return FinancialRecommendationResponse(id=recommendation.id or uuid4(), recommendation_type=recommendation.recommendation_type, title=recommendation.title, action=recommendation.action, risk_domain=recommendation.risk_domain, priority_rank=recommendation.priority_rank, business_impact=recommendation.business_impact, technical_impact=recommendation.technical_impact, metadata=recommendation.recommendation_metadata, created_at=recommendation.created_at or datetime.now(UTC), updated_at=recommendation.updated_at or datetime.now(UTC))

    def _behavior_payload(self, behavior: BehaviorProfile) -> dict[str, object]:
        return {
            "id": str(behavior.id) if behavior.id else None,
            "entity_id": behavior.entity_id,
            "entity_type": behavior.entity_type,
            "baseline_behavior": behavior.baseline_behavior,
            "behavior_deviation": behavior.behavior_deviation,
            "peer_comparison": behavior.peer_comparison,
            "login_pattern": behavior.login_pattern,
            "transaction_pattern": behavior.transaction_pattern,
            "navigation_pattern": behavior.navigation_pattern,
            "device_pattern": behavior.device_pattern,
            "session_pattern": behavior.session_pattern,
            "risk_trend": behavior.risk_trend,
            "metadata": behavior.profile_metadata,
        }

    def _risk_score_payload(self, score: RiskScore) -> dict[str, object]:
        return {
            "id": str(score.id) if score.id else None,
            "entity_id": score.entity_id,
            "overall_financial_risk": score.overall_financial_risk,
            "transaction_risk": score.transaction_risk,
            "customer_risk": score.customer_risk,
            "merchant_risk": score.merchant_risk,
            "account_risk": score.account_risk,
            "identity_risk": score.identity_risk,
            "behavior_risk": score.behavior_risk,
            "device_risk": score.device_risk,
            "aml_risk": score.aml_risk,
            "risk_factors": score.risk_factors,
            "metadata": score.score_metadata,
        }

    def _risk_level(self, score: float) -> str:
        if score >= 80:
            return "critical"
        if score >= 60:
            return "high"
        if score >= 40:
            return "medium"
        return "low"

    def _device_fingerprint(self, request: FraudAnalyzeRequest) -> str:
        payload = "|".join([request.device_id or "device", request.ip_address or "ip", request.location or "location", request.channel, request.customer_id])
        return sha256(payload.encode("utf-8")).hexdigest()[:24]

    async def _cache_get(self, key: str) -> dict[str, object] | None:
        if self.redis_client is None:
            return None
        cached = await self.redis_client.get(key)
        return json.loads(cached) if cached else None

    async def _cache_set(self, key: str, payload: dict[str, object], ttl: int) -> None:
        if self.redis_client is None:
            return
        await self.redis_client.set(key, json.dumps(payload), ex=ttl)

    def _cache_key(self, prefix: str, request: object) -> str:
        return f"{self.settings.banking_redis_cache_prefix}:{prefix}:{sha256(json.dumps(request.model_dump(mode='json'), sort_keys=True, default=str).encode('utf-8')).hexdigest()}"
