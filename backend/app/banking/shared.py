from __future__ import annotations

from collections import Counter, defaultdict
from dataclasses import dataclass, field
from datetime import UTC, datetime, timedelta
from statistics import mean
from typing import Any
from uuid import uuid4

try:
    import networkx as nx  # type: ignore
except Exception:  # pragma: no cover - optional dependency
    nx = None

from app.banking.models import BankingGraphEdge, BankingGraphNode
from app.banking.schemas import AMLAnalyzeRequest, BehaviorDimension, CaseStatus, FraudAnalyzeRequest, FraudCategory, RiskEntityType, TransactionType, UEBAAnalyzeRequest


def _now() -> datetime:
    return datetime.now(UTC)


def _clamp(value: float, lower: float = 0.0, upper: float = 100.0) -> float:
    return max(lower, min(upper, value))


def _normalize(value: str) -> str:
    return "".join(character.lower() for character in value if character.isalnum())


def _slug(value: str) -> str:
    return "-".join(part for part in _normalize(value).split() if part)


def _trend(values: list[float]) -> float:
    if len(values) < 2:
        return 0.0
    return values[-1] - values[0]


@dataclass(slots=True)
class BankingGraphBackend:
    _nodes: dict[str, dict[str, object]] = field(init=False, default_factory=dict)
    _edges: list[dict[str, object]] = field(init=False, default_factory=list)
    _graph: Any | None = field(init=False, default=None)

    def __post_init__(self) -> None:
        self._graph = nx.MultiDiGraph() if nx is not None else None

    def add_node(self, node_key: str, node_type: str, label: str, **properties: object) -> None:
        payload = {"node_type": node_type, "label": label, "properties": properties}
        self._nodes[node_key] = payload
        if self._graph is not None:
            self._graph.add_node(node_key, **payload)

    def add_edge(self, source: str, target: str, relation_type: str, confidence: float = 50.0, **metadata: object) -> None:
        payload = {"source": source, "target": target, "relation_type": relation_type, "confidence": confidence, "metadata": metadata}
        self._edges.append(payload)
        if self._graph is not None:
            self._graph.add_edge(source, target, **payload)

    def shortest_path(self, source: str, target: str) -> list[str]:
        if self._graph is not None and source in self._graph and target in self._graph:
            try:
                return list(nx.shortest_path(self._graph, source, target))
            except Exception:
                return []
        adjacency = defaultdict(list)
        for edge in self._edges:
            adjacency[edge["source"]].append(edge["target"])
        queue = [(source, [source])]
        visited = {source}
        while queue:
            current, path = queue.pop(0)
            if current == target:
                return path
            for neighbor in adjacency.get(current, []):
                if neighbor not in visited:
                    visited.add(neighbor)
                    queue.append((neighbor, path + [neighbor]))
        return []

    def centrality(self) -> dict[str, float]:
        if self._graph is not None and self._graph.number_of_nodes() > 0:
            scores = nx.degree_centrality(self._graph)
            return {node: float(score) for node, score in scores.items()}
        counts = Counter()
        for edge in self._edges:
            counts[edge["source"]] += 1
            counts[edge["target"]] += 1
        total = float(max(1, len(self._nodes)))
        return {node: round(count / total, 4) for node, count in counts.items()}

    def communities(self) -> list[list[str]]:
        if self._graph is not None and self._graph.number_of_nodes() > 0:
            try:
                undirected = self._graph.to_undirected()
                return [list(component) for component in nx.connected_components(undirected)]
            except Exception:
                pass
        clusters: dict[str, list[str]] = defaultdict(list)
        for node_key, node in self._nodes.items():
            clusters[str(node.get("node_type", "entity"))].append(node_key)
        return list(clusters.values())

    def graph(self) -> dict[str, object]:
        return {"nodes": self._nodes, "edges": self._edges}


@dataclass(slots=True)
class BankingIntelligenceEngine:
    def classify_transaction(self, request: Any, history: list[dict[str, object]]) -> dict[str, object]:
        amount_factor = min(float(request.amount) / 10000.0, 25.0)
        type_factor = 12.0 if request.transaction_type in {TransactionType.SWIFT, TransactionType.INTERNATIONAL_TRANSFER} else 6.0
        channel_factor = 10.0 if request.channel.lower() in {"wallet", "mobile", "net_banking"} else 4.0
        history_factor = min(len(history) * 2.0, 14.0)
        risk = _clamp(25.0 + amount_factor + type_factor + channel_factor + history_factor)
        classification = "high_value" if request.amount >= 50000 else "standard"
        if request.transaction_type in {TransactionType.SWIFT, TransactionType.INTERNATIONAL_TRANSFER}:
            classification = "cross_border"
        if request.transaction_type in {TransactionType.CREDIT_CARD, TransactionType.DEBIT_CARD, TransactionType.POS}:
            classification = "card_present" if request.channel.lower() == "pos" else "card_not_present"
        validation_status = "validated" if risk < 80 else "review"
        return {
            "classification": classification,
            "validation_status": validation_status,
            "risk_score": risk,
            "fraud_score": _clamp(risk + (8.0 if request.device_id else 0.0)),
            "aml_score": _clamp(risk + (6.0 if request.amount >= 100000 else 0.0)),
            "enrichment": {
                "amount_bucket": "large" if request.amount >= 50000 else "normal",
                "channel_risk": channel_factor,
                "type_risk": type_factor,
                "history_count": len(history),
            },
        }

    def _aml_patterns(self, request: AMLAnalyzeRequest) -> list[str]:
        patterns: list[str] = []
        if request.cash_transactions >= 5:
            patterns.append("cash_structuring")
        if request.large_cash_amount >= 50000:
            patterns.append("high_value_cash_activity")
        if len(request.countries) >= 3:
            patterns.append("multi_jurisdiction_activity")
        if len(request.counterparties) >= 5:
            patterns.append("counterparty_spread")
        if request.pep_matches and request.sanctions_matches:
            patterns.append("pep_sanctions_overlap")
        if request.watchlist_matches and request.edd_required:
            patterns.append("watchlist_edd_escalation")
        return patterns

    def fraud_analysis(self, request: FraudAnalyzeRequest, profile: dict[str, object], behavior: dict[str, object], device: dict[str, object]) -> dict[str, object]:
        category = request.fraud_category_hint.value if request.fraud_category_hint else self._fraud_category(request)
        velocity = self._velocity_indicator(request)
        anomaly = self._anomaly_indicator(request, profile, behavior, device)
        location = self._location_indicator(request, device)
        merchant = self._merchant_indicator(request)
        account = self._account_indicator(request)
        evidence = self._evidence_bundle(request, velocity, anomaly, location, merchant, account)
        fraud_score = _clamp(30.0 + velocity["score"] + anomaly["score"] + location["score"] + merchant["score"] + account["score"])
        confidence = _clamp(55.0 + len(evidence) * 4.0 + len(request.history) * 1.5)
        recommendations = [
            "Hold or step-up authenticate the transaction.",
            "Verify device and location consistency.",
            "Review linked accounts and merchant exposure.",
        ]
        if fraud_score >= 80:
            recommendations.append("Escalate to fraud investigations immediately.")
        return {
            "fraud_category": category,
            "fraud_score": fraud_score,
            "confidence": confidence,
            "evidence": evidence,
            "behavior_indicators": behavior.get("indicators", []),
            "velocity_indicators": velocity["indicators"],
            "anomaly_indicators": anomaly["indicators"],
            "location_indicators": location["indicators"],
            "merchant_indicators": merchant["indicators"],
            "account_indicators": account["indicators"],
            "linked_transactions": [item.get("transaction_id", request.transaction_id) for item in request.history[:10]],
            "risk_factors": [*velocity["indicators"], *anomaly["indicators"], *location["indicators"], *merchant["indicators"], *account["indicators"]],
            "recommendations": recommendations,
            "business_impact": "Potential customer and institution loss if not contained.",
            "explainability": {
                "fraud_score": fraud_score,
                "confidence": confidence,
                "behavior_indicators": behavior.get("indicators", []),
                "historical_comparison": behavior.get("peer_comparison", {}),
                "linked_transactions": [item.get("transaction_id", request.transaction_id) for item in request.history[:10]],
                "risk_factors": [*velocity["indicators"], *anomaly["indicators"], *location["indicators"], *merchant["indicators"], *account["indicators"]],
                "recommendations": recommendations,
            },
        }

    def aml_analysis(self, request: AMLAnalyzeRequest) -> dict[str, object]:
        alerts = []
        risk_factors = []
        if not request.kyc_validated:
            alerts.append("KYC not validated")
            risk_factors.append("kyc_gap")
        if not request.cdd_complete:
            alerts.append("CDD incomplete")
            risk_factors.append("cdd_gap")
        if request.edd_required:
            alerts.append("EDD required")
            risk_factors.append("edd_trigger")
        if request.pep_matches:
            alerts.append("PEP match detected")
            risk_factors.append("pep_match")
        if request.sanctions_matches:
            alerts.append("Sanctions match detected")
            risk_factors.append("sanctions_match")
        if request.watchlist_matches:
            alerts.append("Watchlist match detected")
            risk_factors.append("watchlist_match")
        suspicious_patterns = self._aml_patterns(request)
        if request.cash_transactions >= 3:
            suspicious_patterns.append("large_cash_activity")
            risk_factors.append("cash_structuring")
        aml_score = _clamp(20.0 + len(alerts) * 12.0 + len(suspicious_patterns) * 8.0 + min(request.large_cash_amount / 10000.0, 20.0))
        case_status = "open" if aml_score >= 60 else "monitor"
        recommendations = [
            "Review KYC and CDD artifacts.",
            "Validate counterparties and source of funds.",
            "Escalate to AML investigations if matches persist.",
        ]
        if aml_score >= 80:
            recommendations.append("Generate a formal AML case and freeze high-risk workflows for review.")
        return {
            "aml_score": aml_score,
            "cdd_status": "complete" if request.cdd_complete else "incomplete",
            "kyc_status": "validated" if request.kyc_validated else "failed",
            "pep_hits": request.pep_matches,
            "sanctions_hits": request.sanctions_matches,
            "watchlist_hits": request.watchlist_matches,
            "suspicious_patterns": suspicious_patterns,
            "alerts": alerts,
            "case_status": case_status,
            "recommendations": recommendations,
            "business_impact": "AML exposure may result in fines, account restrictions, and reputational damage.",
            "risk_factors": risk_factors,
            "metadata": {"cash_transactions": request.cash_transactions, "countries": request.countries, "counterparties": request.counterparties},
        }

    def ueba_analysis(self, request: UEBAAnalyzeRequest) -> dict[str, object]:
        baseline = self._baseline(request)
        deviation = self._deviation(request, baseline)
        peer = self._peer_comparison(request)
        login_pattern = self._pattern_summary(request.login_history, BehaviorDimension.LOGIN_PATTERN)
        transaction_pattern = self._pattern_summary(request.transaction_history, BehaviorDimension.TRANSACTION_PATTERN)
        navigation_pattern = self._pattern_summary(request.navigation_history, BehaviorDimension.NAVIGATION_PATTERN)
        device_pattern = self._pattern_summary(request.device_history, BehaviorDimension.DEVICE_PATTERN)
        session_pattern = self._pattern_summary(request.session_history, BehaviorDimension.SESSION_PATTERN)
        confidence = _clamp(55.0 + deviation["score"] * 0.5 + peer["variance"] * 0.25)
        indicators = [
            f"behavior deviation {deviation['score']:.1f}",
            f"peer variance {peer['variance']:.1f}",
            f"login anomaly {login_pattern['anomaly_score']:.1f}",
        ]
        recommendations = ["Review unusual behavior against baseline.", "Correlate with device and transaction anomalies.", "Escalate if peer deviation persists."]
        return {
            "baseline_behavior": baseline,
            "behavior_deviation": deviation,
            "peer_comparison": peer,
            "login_pattern": login_pattern,
            "transaction_pattern": transaction_pattern,
            "navigation_pattern": navigation_pattern,
            "device_pattern": device_pattern,
            "session_pattern": session_pattern,
            "risk_trend": [{"timestamp": _now() - timedelta(hours=index), "risk": _clamp(confidence + index * 1.5)} for index in range(3)],
            "indicators": indicators,
            "confidence": confidence,
            "recommendations": recommendations,
            "metadata": request.metadata,
        }

    def risk_score(self, transaction_risk: float, customer_risk: float, merchant_risk: float, account_risk: float, identity_risk: float, behavior_risk: float, device_risk: float, aml_risk: float) -> float:
        return _clamp((transaction_risk * 0.2) + (customer_risk * 0.15) + (merchant_risk * 0.1) + (account_risk * 0.15) + (identity_risk * 0.1) + (behavior_risk * 0.1) + (device_risk * 0.1) + (aml_risk * 0.1))

    def investigation(self, request: FraudInvestigateRequest, fraud_bundle: dict[str, object], history: list[dict[str, object]]) -> dict[str, object]:
        linked_accounts = sorted(set(request.linked_accounts + [request.account_id] + [item.get("account_id", request.account_id) for item in history]))
        linked_devices = sorted(set(request.linked_devices + [request.device_id] if request.device_id else request.linked_devices))
        linked_merchants = sorted(set(request.linked_merchants + ([request.merchant_id] if request.merchant_id else [])))
        transaction_timeline = [{"timestamp": item.get("timestamp", _now()), "event": item.get("description", item.get("transaction_id", request.transaction_id)), "amount": float(item.get("amount", request.amount))} for item in history[:10]]
        behavior_timeline = [{"timestamp": _now() - timedelta(hours=index), "event": item} for index, item in enumerate(fraud_bundle.get("behavior_indicators", []), start=1)]
        evidence = [*request.evidence, *fraud_bundle.get("evidence", [])]
        notes = request.analyst_notes or "Investigation generated from fraud intelligence signals."
        analyst_actions = request.analyst_actions or ["Review evidence pack", "Validate linked accounts and devices", "Document disposition"]
        return {
            "case_id": request.case_id or f"case-{request.transaction_id}",
            "fraud_category": fraud_bundle.get("fraud_category", request.fraud_category_hint.value if request.fraud_category_hint else FraudCategory.PAYMENT_FRAUD.value),
            "priority": "high" if float(fraud_bundle.get("fraud_score", 0.0)) >= 70 else "medium",
            "status": CaseStatus.INVESTIGATING.value,
            "evidence": evidence,
            "transaction_timeline": transaction_timeline,
            "behavior_timeline": behavior_timeline,
            "linked_accounts": linked_accounts,
            "linked_devices": linked_devices,
            "linked_merchants": linked_merchants,
            "recommendations": fraud_bundle.get("recommendations", []),
            "investigation_notes": notes,
            "analyst_actions": analyst_actions,
            "business_impact": fraud_bundle.get("business_impact", "Fraud may impact customer funds and operational continuity."),
            "metadata": {"fraud_score": fraud_bundle.get("fraud_score", 0.0), "confidence": fraud_bundle.get("confidence", 0.0)},
        }

    def customer_profile(self, customer_id: str, risk_history: list[dict[str, object]], transaction_history: list[dict[str, object]], behavior_history: list[dict[str, object]]) -> dict[str, object]:
        trust_score = _clamp(75.0 - len([item for item in risk_history if float(item.get("risk", 0.0)) >= 70]) * 8.0)
        fraud_score = _clamp(sum(float(item.get("fraud_score", 0.0)) for item in risk_history) / max(1, len(risk_history)))
        aml_score = _clamp(sum(float(item.get("aml_score", 0.0)) for item in risk_history) / max(1, len(risk_history)))
        compliance_score = _clamp(100.0 - aml_score * 0.5)
        recommendations = ["Maintain ongoing monitoring.", "Increase verification for high-risk transactions.", "Correlate customer behavior with account and device signals."]
        timeline = [{"timestamp": item.get("timestamp", _now()), "event": item.get("transaction_id", customer_id), "risk": float(item.get("risk_score", item.get("risk", 0.0)))} for item in transaction_history[:10]]
        return {
            "customer_profile": {"customer_id": customer_id, "risk_history_count": len(risk_history)},
            "behavior_profile": {"baseline_behavior": self._baseline_from_history(behavior_history), "behavior_deviation": self._behavior_deviation_from_history(behavior_history)},
            "transaction_profile": {"transaction_count": len(transaction_history), "high_value_count": len([item for item in transaction_history if float(item.get("amount", 0.0)) >= 50000])},
            "risk_history": risk_history,
            "trust_score": trust_score,
            "fraud_score": fraud_score,
            "aml_score": aml_score,
            "compliance_score": compliance_score,
            "recommendations": recommendations,
            "customer_timeline": timeline,
            "metadata": {"risk_history_count": len(risk_history), "transaction_history_count": len(transaction_history)},
        }

    def merchant_profile(self, merchant_id: str, transactions: list[dict[str, object]]) -> dict[str, object]:
        chargebacks = len([item for item in transactions if str(item.get("status", "")).lower() in {"chargeback", "reversed"}])
        settlements = len([item for item in transactions if str(item.get("status", "")).lower() in {"settled", "captured"}])
        fraud_exposure = _clamp(20.0 + chargebacks * 12.0 + len([item for item in transactions if float(item.get("risk_score", 0.0)) >= 70]) * 5.0)
        reputation = _clamp(80.0 - chargebacks * 8.0 + settlements * 1.5)
        merchant_risk = _clamp((100.0 - reputation) * 0.6 + fraud_exposure * 0.4)
        recommendations = ["Review chargeback exposure.", "Monitor settlement anomalies.", "Strengthen merchant risk controls."]
        return {
            "merchant_profile": {"merchant_id": merchant_id, "transaction_count": len(transactions)},
            "merchant_category": self._merchant_category(transactions),
            "transaction_history": transactions,
            "chargeback_analysis": {"chargebacks": chargebacks, "rate": chargebacks / max(1, len(transactions))},
            "settlement_analysis": {"settlements": settlements, "rate": settlements / max(1, len(transactions))},
            "fraud_exposure": fraud_exposure,
            "merchant_reputation": reputation,
            "merchant_risk": merchant_risk,
            "recommendations": recommendations,
            "metadata": {"transaction_count": len(transactions)},
        }

    def account_risk(self, account_id: str, transaction_risk: float, behavior_risk: float, device_risk: float, identity_risk: float) -> dict[str, object]:
        account_risk = _clamp((transaction_risk * 0.35) + (behavior_risk * 0.25) + (device_risk * 0.2) + (identity_risk * 0.2))
        return {"account_risk": account_risk, "identity_risk": identity_risk, "behavior_risk": behavior_risk, "device_risk": device_risk, "transaction_risk": transaction_risk, "recommendations": ["Review account access and recent transaction patterns.", "Cross-check with device trust.", "Trigger step-up verification if thresholds are breached."], "metadata": {"account_id": account_id}}

    def graph_seed(self, request: Any, transaction: dict[str, object]) -> tuple[list[dict[str, object]], list[dict[str, object]]]:
        nodes = [
            {"node_key": f"customer:{request.customer_id}", "node_type": "customer", "label": request.customer_id, "properties": {"customer_id": request.customer_id}},
            {"node_key": f"account:{request.account_id}", "node_type": "account", "label": request.account_id, "properties": {"account_id": request.account_id}},
            {"node_key": f"transaction:{request.transaction_id}", "node_type": "transaction", "label": request.transaction_id, "properties": transaction},
        ]
        if getattr(request, "merchant_id", None):
            nodes.append({"node_key": f"merchant:{request.merchant_id}", "node_type": "merchant", "label": request.merchant_id, "properties": {"merchant_id": request.merchant_id}})
        if getattr(request, "device_id", None):
            nodes.append({"node_key": f"device:{request.device_id}", "node_type": "device", "label": request.device_id, "properties": {"device_id": request.device_id}})
        if getattr(request, "ip_address", None):
            nodes.append({"node_key": f"ip:{request.ip_address}", "node_type": "ip_address", "label": request.ip_address, "properties": {"ip_address": request.ip_address}})
        edges = [
            {"source": f"customer:{request.customer_id}", "target": f"account:{request.account_id}", "relation_type": "owns", "confidence": 95.0},
            {"source": f"account:{request.account_id}", "target": f"transaction:{request.transaction_id}", "relation_type": "transfers", "confidence": 90.0},
        ]
        if getattr(request, "merchant_id", None):
            edges.append({"source": f"transaction:{request.transaction_id}", "target": f"merchant:{request.merchant_id}", "relation_type": "pays", "confidence": 88.0})
        if getattr(request, "device_id", None):
            edges.append({"source": f"customer:{request.customer_id}", "target": f"device:{request.device_id}", "relation_type": "uses", "confidence": 86.0})
        if getattr(request, "ip_address", None):
            edges.append({"source": f"device:{request.device_id or request.customer_id}", "target": f"ip:{request.ip_address}", "relation_type": "connected", "confidence": 82.0})
        return nodes, edges

    def dashboard(self, transactions: list[Any], fraud_cases: list[Any], aml_cases: list[Any], ueba_events: list[Any], risk_scores: list[Any]) -> dict[str, object]:
        transaction_count = len(transactions)
        fraud_rate = (len([case for case in fraud_cases if getattr(case, "fraud_score", 0.0) >= 70]) / max(1, transaction_count)) * 100.0
        risk_distribution = {
            "low": len([score for score in risk_scores if float(getattr(score, "overall_financial_risk", 0.0)) < 40]),
            "medium": len([score for score in risk_scores if 40 <= float(getattr(score, "overall_financial_risk", 0.0)) < 70]),
            "high": len([score for score in risk_scores if float(getattr(score, "overall_financial_risk", 0.0)) >= 70]),
        }
        return {"transactions_per_second": float(transaction_count) / 60.0, "fraud_detection_rate": _clamp(fraud_rate), "aml_alerts": len(aml_cases), "ueba_events": len(ueba_events), "false_positives": 0, "false_negatives": 0, "risk_distribution": {key: float(value) for key, value in risk_distribution.items()}, "investigation_time_minutes": 18.0, "fraud_trends": [{"timestamp": _now() - timedelta(days=index), "count": max(0, transaction_count - index * 2)} for index in range(3)], "scorecard": {"transactions": float(transaction_count), "fraud_cases": float(len(fraud_cases)), "aml_cases": float(len(aml_cases)), "ueba_events": float(len(ueba_events))}}

    def _fraud_category(self, request: FraudAnalyzeRequest) -> str:
        text = " ".join([request.description or "", request.channel, request.transaction_type.value, request.metadata.get("merchant_category", "") if request.metadata else ""]).lower()
        if any(term in text for term in ("credential", "login", "password", "device")):
            return FraudCategory.ACCOUNT_TAKEOVER.value
        if any(term in text for term in ("card", "credit", "debit", "pos")):
            return FraudCategory.CARD_FRAUD.value
        if any(term in text for term in ("identity", "synthetic", "kyc")):
            return FraudCategory.IDENTITY_THEFT.value
        if any(term in text for term in ("mule", "cashout", "layering")):
            return FraudCategory.MONEY_MULE.value
        if request.transaction_type == TransactionType.SWIFT or request.transaction_type == TransactionType.INTERNATIONAL_TRANSFER:
            return FraudCategory.WIRE_FRAUD.value
        return request.fraud_category_hint.value if request.fraud_category_hint else FraudCategory.PAYMENT_FRAUD.value

    def _velocity_indicator(self, request: FraudAnalyzeRequest) -> dict[str, object]:
        recent = [item for item in request.history if item.get("customer_id", request.customer_id) == request.customer_id]
        velocity_count = len(recent)
        indicators = []
        score = min(velocity_count * 4.0, 20.0)
        if velocity_count >= 5:
            indicators.append("velocity_spike")
        if any(float(item.get("amount", 0.0)) >= request.amount for item in recent[-3:]):
            indicators.append("burst_growth")
            score += 4.0
        return {"score": score, "indicators": indicators}

    def _anomaly_indicator(self, request: FraudAnalyzeRequest, profile: dict[str, object], behavior: dict[str, object], device: dict[str, object]) -> dict[str, object]:
        score = 0.0
        indicators = []
        if behavior.get("behavior_deviation", {}).get("score", 0.0) >= 60:
            score += 16.0
            indicators.append("behavior_deviation")
        if float(device.get("device_risk", 0.0)) >= 60:
            score += 12.0
            indicators.append("untrusted_device")
        if float(profile.get("trust_score", 50.0)) <= 40:
            score += 10.0
            indicators.append("low_trust_history")
        return {"score": score, "indicators": indicators}

    def _location_indicator(self, request: FraudAnalyzeRequest, device: dict[str, object]) -> dict[str, object]:
        indicators = []
        score = 0.0
        if request.location and device.get("location") and _normalize(request.location) != _normalize(str(device.get("location"))):
            indicators.append("location_mismatch")
            score += 10.0
        if request.ip_address and str(device.get("ip_address") or "") != request.ip_address:
            indicators.append("ip_change")
            score += 8.0
        return {"score": score, "indicators": indicators}

    def _merchant_indicator(self, request: FraudAnalyzeRequest) -> dict[str, object]:
        indicators = []
        score = 0.0
        merchant_category = str(request.metadata.get("merchant_category", "")).lower()
        if request.merchant_id:
            indicators.append("merchant_present")
        if merchant_category in {"high_risk", "crypto", "gaming"}:
            indicators.append("high_risk_merchant_category")
            score += 8.0
        if len(request.linked_merchants) > 3:
            indicators.append("merchant_network_breadth")
            score += 6.0
        return {"score": score, "indicators": indicators}

    def _account_indicator(self, request: FraudAnalyzeRequest) -> dict[str, object]:
        indicators = []
        score = 0.0
        if len(request.linked_accounts) > 2:
            indicators.append("linked_account_breadth")
            score += 10.0
        if any(term in request.transaction_type.value for term in ("wire", "swift")):
            indicators.append("high_value_transfer_path")
            score += 6.0
        return {"score": score, "indicators": indicators}

    def _evidence_bundle(self, request: FraudAnalyzeRequest, *bundles: dict[str, object]) -> list[dict[str, object]]:
        evidence = [{"type": bundle["indicators"][0] if bundle["indicators"] else "signal", "score": float(bundle["score"]), "description": ", ".join(bundle["indicators"]) or "signal observed"} for bundle in bundles if bundle["score"] > 0]
        if request.aml_flags:
            evidence.append({"type": "aml_flag", "score": 10.0, "description": ", ".join(request.aml_flags)})
        return evidence

    def _baseline(self, request: UEBAAnalyzeRequest) -> dict[str, object]:
        return {"login_frequency": len(request.login_history) / 7.0 if request.login_history else 1.0, "transaction_frequency": len(request.transaction_history) / 7.0 if request.transaction_history else 1.0, "device_diversity": len({str(item.get("device_id", "")) for item in request.device_history if item})}

    def _deviation(self, request: UEBAAnalyzeRequest, baseline: dict[str, object]) -> dict[str, object]:
        transaction_volume = sum(float(item.get("amount", 0.0)) for item in request.transaction_history)
        anomaly_score = _clamp(20.0 + len(request.login_history) * 3.0 + len(request.transaction_history) * 2.0 + (transaction_volume / 50000.0))
        return {"score": anomaly_score, "factors": ["login_shift" if len(request.login_history) > 5 else "stable_login", "transaction_volume" if transaction_volume > 0 else "no_volume"], "baseline": baseline}

    def _peer_comparison(self, request: UEBAAnalyzeRequest) -> dict[str, object]:
        peers = [float(item.get("risk", 50.0)) for item in request.peer_history] or [50.0]
        variance = abs(mean(peers) - 50.0)
        return {"peer_average": mean(peers), "variance": variance, "peer_count": len(peers)}

    def _pattern_summary(self, history: list[dict[str, object]], dimension: BehaviorDimension) -> dict[str, object]:
        count = len(history)
        anomaly_score = _clamp(count * 4.0 + sum(float(item.get("risk", 0.0)) for item in history[:5]) * 0.1)
        return {"dimension": dimension.value, "count": count, "anomaly_score": anomaly_score, "recent": history[:5]}

    def _baseline_from_history(self, history: list[dict[str, object]]) -> dict[str, object]:
        return {"count": len(history), "average_risk": mean([float(item.get("risk", 50.0)) for item in history]) if history else 50.0}

    def _behavior_deviation_from_history(self, history: list[dict[str, object]]) -> dict[str, object]:
        risk_values = [float(item.get("risk", 50.0)) for item in history]
        return {"score": _clamp(20.0 + sum(risk_values) / max(1, len(risk_values))), "trend": _trend(risk_values), "samples": len(risk_values)}

    def _merchant_category(self, transactions: list[dict[str, object]]) -> str:
        categories = Counter(str(item.get("merchant_category", "general")).lower() for item in transactions)
        return categories.most_common(1)[0][0] if categories else "general"


def build_graph_backend(nodes: list[dict[str, object]], edges: list[dict[str, object]]) -> BankingGraphBackend:
    backend = BankingGraphBackend()
    for node in nodes:
        backend.add_node(str(node["node_key"]), str(node.get("node_type", "entity")), str(node.get("label", node["node_key"])), **dict(node.get("properties") or {}))
    for edge in edges:
        backend.add_edge(str(edge["source"]), str(edge["target"]), str(edge.get("relation_type", "related")), float(edge.get("confidence", 50.0)), **dict(edge.get("metadata") or {}))
    return backend
