from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from sqlalchemy.ext.asyncio import AsyncSession

from app.banking.models import AMLCase, BankingGraphEdge, BankingGraphNode, BehaviorProfile, CustomerProfile, DeviceProfile, FinancialRecommendation, FraudCase, IdentityProfile, MerchantProfile, RiskScore, Transaction


@dataclass(slots=True)
class BankingRepository:
    session: AsyncSession | None = None
    transactions: list[Transaction] = field(default_factory=list)
    customer_profiles: list[CustomerProfile] = field(default_factory=list)
    merchant_profiles: list[MerchantProfile] = field(default_factory=list)
    behavior_profiles: list[BehaviorProfile] = field(default_factory=list)
    fraud_cases: list[FraudCase] = field(default_factory=list)
    aml_cases: list[AMLCase] = field(default_factory=list)
    risk_scores: list[RiskScore] = field(default_factory=list)
    device_profiles: list[DeviceProfile] = field(default_factory=list)
    identity_profiles: list[IdentityProfile] = field(default_factory=list)
    financial_recommendations: list[FinancialRecommendation] = field(default_factory=list)
    graph_nodes: list[BankingGraphNode] = field(default_factory=list)
    graph_edges: list[BankingGraphEdge] = field(default_factory=list)

    async def add_transaction(self, transaction: Transaction) -> Transaction:
        return await self._store(self.transactions, transaction)

    async def add_customer_profile(self, profile: CustomerProfile) -> CustomerProfile:
        return await self._store(self.customer_profiles, profile)

    async def add_merchant_profile(self, profile: MerchantProfile) -> MerchantProfile:
        return await self._store(self.merchant_profiles, profile)

    async def add_behavior_profile(self, profile: BehaviorProfile) -> BehaviorProfile:
        return await self._store(self.behavior_profiles, profile)

    async def add_fraud_case(self, case: FraudCase) -> FraudCase:
        return await self._store(self.fraud_cases, case)

    async def add_aml_case(self, case: AMLCase) -> AMLCase:
        return await self._store(self.aml_cases, case)

    async def add_risk_score(self, score: RiskScore) -> RiskScore:
        return await self._store(self.risk_scores, score)

    async def add_device_profile(self, profile: DeviceProfile) -> DeviceProfile:
        return await self._store(self.device_profiles, profile)

    async def add_identity_profile(self, profile: IdentityProfile) -> IdentityProfile:
        return await self._store(self.identity_profiles, profile)

    async def add_recommendation(self, recommendation: FinancialRecommendation) -> FinancialRecommendation:
        return await self._store(self.financial_recommendations, recommendation)

    async def add_graph_node(self, node: BankingGraphNode) -> BankingGraphNode:
        return await self._store(self.graph_nodes, node)

    async def add_graph_edge(self, edge: BankingGraphEdge) -> BankingGraphEdge:
        return await self._store(self.graph_edges, edge)

    async def list_transactions(self) -> list[Transaction]:
        return list(self.transactions)

    async def list_customers(self) -> list[CustomerProfile]:
        return list(self.customer_profiles)

    async def list_merchants(self) -> list[MerchantProfile]:
        return list(self.merchant_profiles)

    async def list_behaviors(self) -> list[BehaviorProfile]:
        return list(self.behavior_profiles)

    async def list_fraud_cases(self) -> list[FraudCase]:
        return list(self.fraud_cases)

    async def list_aml_cases(self) -> list[AMLCase]:
        return list(self.aml_cases)

    async def list_risk_scores(self) -> list[RiskScore]:
        return list(self.risk_scores)

    async def list_devices(self) -> list[DeviceProfile]:
        return list(self.device_profiles)

    async def list_identities(self) -> list[IdentityProfile]:
        return list(self.identity_profiles)

    async def list_recommendations(self) -> list[FinancialRecommendation]:
        return list(self.financial_recommendations)

    async def _store(self, collection: list[Any], record: Any) -> Any:
        if self.session is None:
            collection.append(record)
            return record
        self.session.add(record)
        await self.session.flush()
        collection.append(record)
        return record
