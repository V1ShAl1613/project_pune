from __future__ import annotations

import logging

from app.banking.dependencies import provide_banking_service
from app.banking.repositories.banking_repository import BankingRepository
from app.banking.schemas import AMLAnalyzeRequest, BankingTransactionRequest, FraudAnalyzeRequest, FraudInvestigateRequest, TransactionType, UEBAAnalyzeRequest
from app.banking.services.banking_service import BankingService
from app.core.settings import TestingSettings


class _FakeBankingService:
    def __init__(self) -> None:
        self.service = BankingService(repository=BankingRepository(), settings=TestingSettings(), redis_client=None, logger=logging.getLogger("test"))

    async def analyze_transaction(self, payload):
        return await self.service.analyze_transaction(payload)

    async def analyze_fraud(self, payload):
        return await self.service.analyze_fraud(payload)

    async def score_fraud(self, payload):
        return await self.service.score_fraud(payload)

    async def investigate_fraud(self, payload):
        return await self.service.investigate_fraud(payload)

    async def analyze_aml(self, payload):
        return await self.service.analyze_aml(payload)

    async def analyze_ueba(self, payload):
        return await self.service.analyze_ueba(payload)

    async def customer_risk(self, payload):
        return await self.service.customer_risk(payload)

    async def merchant_risk(self, payload):
        return await self.service.merchant_risk(payload)

    async def account_risk(self, payload):
        return await self.service.account_risk(payload)

    async def risk_dashboard(self):
        return await self.service.risk_dashboard()

    async def fraud_cases(self):
        return []

    async def transaction_search(self, payload):
        return await self.service.transaction_search(payload)

    async def financial_recommendations(self):
        return []


def test_fraud_analyze_route_is_registered(client, app) -> None:
    app.dependency_overrides[provide_banking_service] = lambda: _FakeBankingService()
    try:
        response = client.post(
            "/fraud/analyze",
            json={
                "transaction_id": "txn-1001",
                "customer_id": "cust-1",
                "account_id": "acc-1",
                "amount": 125000,
                "transaction_type": TransactionType.UPI.value,
                "channel": "mobile",
                "merchant_id": "merch-1",
                "device_id": "dev-1",
                "ip_address": "203.0.113.10",
                "location": "Mumbai",
                "history": [{"transaction_id": "txn-1000", "risk_score": 75, "amount": 10000}],
            },
        )
    finally:
        app.dependency_overrides.clear()

    assert response.status_code == 200
    payload = response.json()
    assert payload["transaction_id"] == "txn-1001"
    assert payload["fraud_score"] >= 0
    assert payload["confidence"] >= 0


def test_aml_and_ueba_routes_return_scores(client, app) -> None:
    app.dependency_overrides[provide_banking_service] = lambda: _FakeBankingService()
    try:
        aml_response = client.post(
            "/aml/analyze",
            json={
                "customer_id": "cust-aml",
                "account_id": "acc-aml",
                "kyc_validated": False,
                "cdd_complete": False,
                "pep_matches": ["pep-1"],
                "sanctions_matches": ["sanction-1"],
                "cash_transactions": 5,
                "large_cash_amount": 250000,
            },
        )
        ueba_response = client.post(
            "/ueba/analyze",
            json={
                "entity_id": "cust-ueba",
                "entity_type": "customer",
                "login_history": [{"risk": 70}],
                "transaction_history": [{"amount": 12000, "risk": 75}],
                "device_history": [{"device_id": "dev-1", "risk": 80}],
            },
        )
    finally:
        app.dependency_overrides.clear()

    assert aml_response.status_code == 200
    assert ueba_response.status_code == 200
    assert aml_response.json()["aml_score"] >= 0
    assert ueba_response.json()["confidence"] >= 0


def test_transaction_and_risk_dashboard_flow() -> None:
    service = BankingService(repository=BankingRepository(), settings=TestingSettings(), redis_client=None, logger=logging.getLogger("test"))
    transaction = __import__("asyncio").run(
        service.analyze_transaction(
            BankingTransactionRequest(
                transaction_id="txn-2001",
                customer_id="cust-200",
                account_id="acc-200",
                amount=25000,
                transaction_type=TransactionType.NEFT,
            )
        )
    )
    fraud = __import__("asyncio").run(
        service.analyze_fraud(
            FraudAnalyzeRequest(
                transaction_id="txn-2001",
                customer_id="cust-200",
                account_id="acc-200",
                amount=25000,
                transaction_type=TransactionType.NEFT,
                device_id="device-200",
            )
        )
    )
    investigation = __import__("asyncio").run(
        service.investigate_fraud(
            FraudInvestigateRequest(
                transaction_id="txn-2001",
                customer_id="cust-200",
                account_id="acc-200",
                amount=25000,
                transaction_type=TransactionType.NEFT,
                device_id="device-200",
                analyst_notes="review case",
            )
        )
    )
    dashboard = __import__("asyncio").run(service.risk_dashboard())

    assert transaction.transaction_id == "txn-2001"
    assert fraud.fraud_score >= 0
    assert investigation.case_id
    assert dashboard.fraud_detection_rate >= 0
