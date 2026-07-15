from __future__ import annotations

from fastapi import APIRouter, Depends

from app.banking.dependencies import provide_banking_service
from app.banking.schemas import (
    AMLAnalyzeRequest,
    AMLAnalysisResponse,
    AccountRiskLookupRequest,
    AccountRiskResponse,
    BankingTransactionRequest,
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
    TransactionResponse,
    TransactionSearchRequest,
    TransactionSearchResponse,
    UEBAAnalyzeRequest,
    UEBAAnalysisResponse,
)
from app.banking.services.banking_service import BankingService


router = APIRouter(tags=["banking-intelligence"])


@router.post("/transactions/analyze", response_model=TransactionResponse)
async def analyze_transaction(payload: BankingTransactionRequest, banking_service: BankingService = Depends(provide_banking_service)) -> TransactionResponse:
    return await banking_service.analyze_transaction(payload)


@router.post("/fraud/analyze", response_model=FraudAnalysisResponse)
async def analyze_fraud(payload: FraudAnalyzeRequest, banking_service: BankingService = Depends(provide_banking_service)) -> FraudAnalysisResponse:
    return await banking_service.analyze_fraud(payload)


@router.post("/fraud/score", response_model=FraudScoreResponse)
async def score_fraud(payload: FraudScoreRequest, banking_service: BankingService = Depends(provide_banking_service)) -> FraudScoreResponse:
    return await banking_service.score_fraud(payload)


@router.post("/fraud/investigate", response_model=FraudCaseResponse)
async def investigate_fraud(payload: FraudInvestigateRequest, banking_service: BankingService = Depends(provide_banking_service)) -> FraudCaseResponse:
    return await banking_service.investigate_fraud(payload)


@router.post("/aml/analyze", response_model=AMLAnalysisResponse)
async def analyze_aml(payload: AMLAnalyzeRequest, banking_service: BankingService = Depends(provide_banking_service)) -> AMLAnalysisResponse:
    return await banking_service.analyze_aml(payload)


@router.post("/ueba/analyze", response_model=UEBAAnalysisResponse)
async def analyze_ueba(payload: UEBAAnalyzeRequest, banking_service: BankingService = Depends(provide_banking_service)) -> UEBAAnalysisResponse:
    return await banking_service.analyze_ueba(payload)


@router.get("/customers/{id}/risk", response_model=CustomerRiskResponse)
async def customer_risk(id: str, banking_service: BankingService = Depends(provide_banking_service)) -> CustomerRiskResponse:
    return await banking_service.customer_risk(CustomerRiskLookupRequest(customer_id=id))


@router.get("/merchants/{id}/risk", response_model=MerchantRiskResponse)
async def merchant_risk(id: str, banking_service: BankingService = Depends(provide_banking_service)) -> MerchantRiskResponse:
    return await banking_service.merchant_risk(MerchantRiskLookupRequest(merchant_id=id))


@router.get("/accounts/{id}/risk", response_model=AccountRiskResponse)
async def account_risk(id: str, banking_service: BankingService = Depends(provide_banking_service)) -> AccountRiskResponse:
    return await banking_service.account_risk(AccountRiskLookupRequest(account_id=id))


@router.get("/risk/dashboard", response_model=RiskDashboardResponse)
async def risk_dashboard(banking_service: BankingService = Depends(provide_banking_service)) -> RiskDashboardResponse:
    return await banking_service.risk_dashboard()


@router.get("/fraud/cases", response_model=list[FraudCaseResponse])
async def fraud_cases(banking_service: BankingService = Depends(provide_banking_service)) -> list[FraudCaseResponse]:
    return await banking_service.fraud_cases()


@router.post("/transactions/search", response_model=TransactionSearchResponse)
async def search_transactions(payload: TransactionSearchRequest, banking_service: BankingService = Depends(provide_banking_service)) -> TransactionSearchResponse:
    return await banking_service.transaction_search(payload)


@router.get("/financial/recommendations", response_model=list[FinancialRecommendationResponse])
async def financial_recommendations(banking_service: BankingService = Depends(provide_banking_service)) -> list[FinancialRecommendationResponse]:
    return await banking_service.financial_recommendations()
