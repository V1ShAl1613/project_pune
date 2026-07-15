from __future__ import annotations

import hashlib
import re
from collections import Counter, defaultdict
from dataclasses import dataclass, field
from datetime import UTC, datetime, timedelta
from hashlib import sha256
from statistics import mean
from typing import Any
from uuid import uuid4

try:
    import networkx as nx  # type: ignore
except Exception:  # pragma: no cover - optional dependency
    nx = None

from app.threat.models import IOC, MITREMapping, ThreatActor, ThreatCampaign
from app.threat.schemas import GraphQueryType, IOCType, ThreatAnalysisRequest, ThreatCorrelateRequest, ThreatHuntRequest, ThreatHuntType, ThreatMetricsResponse


def _now() -> datetime:
    return datetime.now(UTC)


def _clamp(value: float, lower: float = 0.0, upper: float = 100.0) -> float:
    return max(lower, min(upper, value))


def _normalize(value: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", value.lower()).strip("-")


def _tokenize(value: str) -> set[str]:
    return {token for token in re.findall(r"[a-z0-9_.:/@-]+", value.lower()) if len(token) > 1}


def _fingerprint(value: str) -> str:
    return sha256(value.strip().lower().encode("utf-8")).hexdigest()[:16]


def _ioc_type(indicator: str) -> str:
    text = indicator.strip().lower()
    if re.match(r"^https?://", text):
        return IOCType.URL.value
    if re.match(r"^(?:[a-z0-9-]+\.)+[a-z]{2,}$", text):
        return IOCType.DOMAIN.value
    if re.match(r"^(?:[a-f0-9]{32}|[a-f0-9]{40}|[a-f0-9]{64})$", text):
        return IOCType.HASH.value
    if re.match(r"^[^@\s]+@[^@\s]+\.[^@\s]+$", text):
        return IOCType.EMAIL.value
    if re.match(r"^(?:\d{1,3}\.){3}\d{1,3}$", text):
        return IOCType.IP.value
    if text.startswith("sha") or "certificate" in text:
        return IOCType.CERTIFICATE.value
    if "registry" in text:
        return IOCType.REGISTRY.value
    if "mutex" in text:
        return IOCType.MUTEX.value
    if "process" in text:
        return IOCType.PROCESS.value
    if "container" in text:
        return IOCType.CONTAINER.value
    if "kubernetes" in text or text.startswith("k8s"):
        return IOCType.KUBERNETES_OBJECT.value
    if "cloud" in text or "aws:" in text or "azure:" in text or "gcp:" in text:
        return IOCType.CLOUD_RESOURCE.value
    if "api key" in text or text.startswith("sk-"):
        return IOCType.API_KEY.value
    return IOCType.FILE.value


def _kill_chain_stage(text: str) -> str:
    normalized = text.lower()
    if any(keyword in normalized for keyword in ("scan", "recon", "survey", "enumerat")):
        return "reconnaissance"
    if any(keyword in normalized for keyword in ("weapon", "payload", "exploit kit")):
        return "weaponization"
    if any(keyword in normalized for keyword in ("deliver", "phish", "email", "malicious url")):
        return "delivery"
    if any(keyword in normalized for keyword in ("exploit", "vulnerability", "rce", "privilege")):
        return "exploitation"
    if any(keyword in normalized for keyword in ("install", "persist", "startup", "service")):
        return "installation"
    if any(keyword in normalized for keyword in ("c2", "command and control", "beacon", "callback")):
        return "command_and_control"
    return "actions_on_objectives"


def _diamond_model(actor: str, infrastructure: list[str], capability: list[str], victim: str, evidence: list[dict[str, object]]) -> dict[str, object]:
    return {
        "adversary": actor,
        "infrastructure": infrastructure,
        "capability": capability,
        "victim": victim,
        "relationships": [
            {"from": actor, "to": victim, "type": "targets"},
            {"from": actor, "to": ", ".join(infrastructure) if infrastructure else "unknown", "type": "uses"},
            {"from": ", ".join(capability) if capability else "unknown", "to": victim, "type": "enables"},
        ],
        "confidence": _clamp(mean([float(item.get("score", 50.0)) for item in evidence]) if evidence else 50.0),
        "evidence_count": len(evidence),
        "timeline": [item.get("timestamp") for item in evidence if item.get("timestamp")],
    }


@dataclass(slots=True)
class GraphBackend:
    """Graph backend using NetworkX when available and a deterministic fallback otherwise."""

    _nodes: dict[str, dict[str, object]] = field(init=False, default_factory=dict)
    _edges: list[dict[str, object]] = field(init=False, default_factory=list)
    _graph: Any | None = field(init=False, default=None)

    def __post_init__(self) -> None:
        self._graph = nx.DiGraph() if nx is not None else None

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
            clusters[str(node.get("node_type", "unknown"))].append(node_key)
        return list(clusters.values())

    def graph(self) -> dict[str, object]:
        return {"nodes": self._nodes, "edges": self._edges}


@dataclass(slots=True)
class ThreatIntelEngine:
    """Deterministic SOC intelligence engine with explainable threat analytics."""

    def build_mitre_matrix(self, request: ThreatAnalysisRequest) -> list[dict[str, object]]:
        tokens = _tokenize(" ".join([request.query, *request.mitre_techniques, *request.mitre_tactics, *request.atlas_techniques]))
        matrix: list[dict[str, object]] = []
        for technique in self._technique_candidates(tokens, request):
            matrix.append(technique)
        if not matrix:
            matrix.append(self._default_mapping(request.query))
        return matrix

    def analyze(self, request: ThreatAnalysisRequest, graph_backend: GraphBackend, evidence: list[dict[str, object]]) -> dict[str, object]:
        iocs = self.normalize_iocs(request.iocs, request.indicators, evidence)
        mitre_mappings = self.build_mitre_matrix(request)
        atlas_mappings = self._atlas_mappings(request)
        kill_chain = _kill_chain_stage(request.query + " " + request.technical_context if request.technical_context else request.query)
        diamond = _diamond_model(self._infer_actor(request, iocs), [ioc["indicator"] for ioc in iocs[:3]], request.mitre_techniques[:3] or [mitre_mappings[0]["technique"]], request.assets[0] if request.assets else request.query, evidence)
        attack_paths = self._attack_paths(request, graph_backend, iocs)
        correlations = self.correlate(request, iocs, evidence)
        threat_actors = self._actors_from_request(request, iocs, mitre_mappings)
        campaigns = self._campaigns_from_request(request, iocs, mitre_mappings)
        graph_relationships = self._graph_relationships(request, iocs, attack_paths, correlations)
        confidence = self._confidence_score(request, iocs, evidence, mitre_mappings, correlations)
        recommendations = self._recommendations(request, confidence, kill_chain, iocs, attack_paths)
        business_impact = f"{kill_chain.replace('_', ' ').title()} risk affecting {len(request.assets) or 1} assets and {len(iocs)} indicators"
        technical_impact = f"{len(mitre_mappings)} MITRE mappings and {len(graph_relationships)} graph relationships identified"
        timeline = self._timeline(request, iocs, correlations)
        explainability = {
            "evidence": evidence,
            "mitre_mapping": mitre_mappings,
            "kill_chain_stage": kill_chain,
            "diamond_model": diamond,
            "graph_relationships": graph_relationships,
            "confidence": confidence,
            "recommendations": recommendations,
            "business_impact": business_impact,
        }
        return {
            "evidence": evidence,
            "mitre_mappings": mitre_mappings,
            "mitre_atlas_mappings": atlas_mappings,
            "kill_chain_stage": kill_chain,
            "diamond_model": diamond,
            "graph_relationships": graph_relationships,
            "attack_paths": attack_paths,
            "correlations": correlations,
            "iocs": iocs,
            "threat_actors": threat_actors,
            "campaigns": campaigns,
            "confidence": confidence["overall_confidence"],
            "confidence_breakdown": confidence,
            "recommendations": recommendations,
            "business_impact": business_impact,
            "technical_impact": technical_impact,
            "timeline": timeline,
            "explainability": explainability,
        }

    def correlate(self, request: ThreatCorrelateRequest | ThreatAnalysisRequest, iocs: list[dict[str, object]], evidence: list[dict[str, object]]) -> list[dict[str, object]]:
        correlations: list[dict[str, object]] = []
        entity_values = [*request.assets, *request.users, *request.organizations, *request.iocs, *[item["indicator"] for item in iocs]]
        for entity in entity_values[:20]:
            related = [indicator["indicator"] for indicator in iocs if _normalize(indicator["indicator"]).find(_normalize(str(entity))) >= 0 or _normalize(str(entity)).find(_normalize(indicator["indicator"])) >= 0]
            if related or evidence:
                correlations.append(
                    {
                        "correlation_type": "ioc_entity" if related else "behavioral",
                        "entity_type": self._entity_type(entity),
                        "entity_value": str(entity),
                        "confidence": _clamp(60.0 + len(related) * 8.0 + len(evidence) * 2.0),
                        "evidence_count": len(evidence),
                        "related_entities": related or [item["indicator"] for item in iocs[:3]],
                        "timeline": self._timeline(request, iocs, []),
                        "attribution": self._infer_actor(request, iocs),
                        "correlation_metadata": {"source": "deterministic"},
                    }
                )
        if not correlations:
            correlations.append(
                {
                    "correlation_type": "contextual",
                    "entity_type": "query",
                    "entity_value": request.query,
                    "confidence": 55.0,
                    "evidence_count": len(evidence),
                    "related_entities": [item["indicator"] for item in iocs[:3]],
                    "timeline": self._timeline(request, iocs, []),
                    "attribution": None,
                    "correlation_metadata": {"source": "fallback"},
                }
            )
        return correlations

    def hunt(self, request: ThreatHuntRequest, iocs: list[dict[str, object]], graph_backend: GraphBackend, evidence: list[dict[str, object]]) -> dict[str, object]:
        findings = []
        mitre = self.build_mitre_matrix(request)
        for ioc in iocs[: request.limit]:
            findings.append(
                {
                    "finding_type": request.hunt_type.value,
                    "indicator": ioc["indicator"],
                    "indicator_type": ioc["indicator_type"],
                    "confidence": _clamp(ioc["confidence"] + len(evidence) * 2.0),
                    "mitre": mitre[0],
                    "graph_node": ioc["normalized_indicator"],
                }
            )
        if not findings:
            findings.append({"finding_type": request.hunt_type.value, "indicator": request.query, "indicator_type": "query", "confidence": 50.0, "mitre": mitre[0], "graph_node": _normalize(request.query)})
        recommendations = self._recommendations(request, self._confidence_score(request, iocs, evidence, mitre, []), _kill_chain_stage(request.query), iocs, [])
        return {
            "findings": findings,
            "mitre_mappings": mitre,
            "iocs": iocs,
            "graph_relationships": self._graph_relationships(request, iocs, [], []),
            "recommendations": recommendations,
            "business_impact": f"{request.hunt_type.value.title()} hunt identified {len(findings)} findings",
            "confidence": self._confidence_score(request, iocs, evidence, mitre, [])["overall_confidence"],
            "hunt_metadata": {"scheduled": request.scheduled, "lookback_hours": request.lookback_hours},
        }

    def graph_query(self, request: GraphQueryRequest, graph_backend: GraphBackend) -> dict[str, object]:
        graph = graph_backend.graph()
        nodes = [{"node_key": key, **value} for key, value in graph["nodes"].items()]
        edges = graph["edges"]
        shortest_path = graph_backend.shortest_path(request.source or request.query, request.target or request.query) if request.query_type in {GraphQueryType.SHORTEST_PATH, GraphQueryType.ATTACK_PATH} else []
        return {
            "query": request.query,
            "query_type": request.query_type.value,
            "nodes": nodes,
            "edges": edges,
            "shortest_path": shortest_path,
            "centrality": graph_backend.centrality(),
            "communities": graph_backend.communities(),
            "risk_propagation": self._risk_propagation(nodes, edges),
            "influence": {node["node_key"]: graph_backend.centrality().get(node["node_key"], 0.0) for node in nodes[:10]},
            "metadata": {"filters": request.filters, "limit": request.limit},
        }

    def graph_path(self, source: str, target: str, graph_backend: GraphBackend) -> dict[str, object]:
        shortest_path = graph_backend.shortest_path(source, target)
        return {"source": source, "target": target, "shortest_path": shortest_path, "attack_chain": [{"node": item, "step": index + 1} for index, item in enumerate(shortest_path)], "confidence": 75.0 if shortest_path else 40.0}

    def search_iocs(self, query: str, iocs: list[dict[str, object]], limit: int = 25, indicator_type: str | None = None) -> list[dict[str, object]]:
        normalized_query = _normalize(query)
        matched = [ioc for ioc in iocs if normalized_query in _normalize(ioc["indicator"]) or normalized_query in _normalize(ioc.get("description") or "")]
        if indicator_type:
            matched = [ioc for ioc in matched if ioc["indicator_type"] == indicator_type]
        return matched[:limit]

    def attack_path(self, request: AttackPathAnalyzeRequest, graph_backend: GraphBackend, iocs: list[dict[str, object]]) -> dict[str, object]:
        chain = [
            {"stage": "reconnaissance", "description": f"Observe exposure around {request.source_asset}"},
            {"stage": "delivery", "description": f"Deliver payload toward {request.target_asset}"},
            {"stage": "exploitation", "description": f"Exploit reachable assets in the path from {request.source_asset} to {request.target_asset}"},
            {"stage": "lateral_movement", "description": "Pivot across identity and infrastructure trust boundaries"},
            {"stage": "exfiltration", "description": f"Exfiltrate data from {request.target_asset}"},
        ]
        confidence = _clamp(60.0 + len(iocs) * 5.0 + len(request.assets) * 2.0)
        return {
            "attack_chain": chain,
            "lateral_movement": ["identity pivot", "service trust abuse"],
            "privilege_escalation": ["token theft", "role abuse"],
            "identity_compromise": [request.source_asset, request.target_asset],
            "cloud_attack_path": [asset for asset in request.assets if any(term in asset.lower() for term in ("cloud", "k8s", "container"))],
            "endpoint_attack_path": [asset for asset in request.assets if any(term in asset.lower() for term in ("endpoint", "host", "device"))],
            "data_exfiltration": [request.target_asset],
            "critical_asset_exposure": [request.target_asset],
            "business_impact": f"Potential impact to {request.target_asset} with {len(chain)} attack stages",
            "likelihood": confidence,
            "confidence": confidence,
            "attack_path_metadata": {"iocs": len(iocs), "relationships": len(graph_backend.graph()["edges"])},
        }

    def metrics(self, total_threats: int, total_iocs: int, total_correlations: int, total_hunts: int, total_attack_paths: int, confidences: list[float], hunt_results: list[dict[str, object]], graph_backend: GraphBackend, mitre_count: int) -> dict[str, object]:
        confidence_average = mean(confidences) if confidences else 0.0
        mitre_coverage = _clamp(min(100.0, mitre_count * 10.0 + total_threats * 2.0))
        detection_accuracy = _clamp(55.0 + total_correlations * 3.0 + total_hunts * 2.0)
        risk_trend = _clamp(50.0 + total_attack_paths * 3.0)
        correlation_rate = _clamp((total_correlations / max(1, total_iocs)) * 100.0)
        hunt_success_rate = _clamp((len([item for item in hunt_results if item.get("findings")]) / max(1, total_hunts)) * 100.0)
        return {
            "total_threats": total_threats,
            "total_iocs": total_iocs,
            "total_correlations": total_correlations,
            "total_hunts": total_hunts,
            "total_attack_paths": total_attack_paths,
            "mitre_coverage": mitre_coverage,
            "detection_accuracy": detection_accuracy,
            "confidence_average": confidence_average,
            "risk_trend": risk_trend,
            "correlation_rate": correlation_rate,
            "hunt_success_rate": hunt_success_rate,
            "graph_health": {"nodes": len(graph_backend.graph()["nodes"]), "edges": len(graph_backend.graph()["edges"])},
            "scorecard": {
                "mitre_coverage": mitre_coverage,
                "detection_accuracy": detection_accuracy,
                "confidence_average": confidence_average,
                "risk_trend": risk_trend,
                "correlation_rate": correlation_rate,
                "hunt_success_rate": hunt_success_rate,
            },
        }

    def normalize_iocs(self, iocs: list[str], indicators: list[dict[str, object]], evidence: list[dict[str, object]]) -> list[dict[str, object]]:
        combined: list[dict[str, object]] = []
        for indicator in iocs:
            combined.append(self._ioc_payload(indicator, source="request"))
        for item in indicators:
            combined.append(self._ioc_payload(str(item.get("indicator") or item.get("value") or item.get("ioc") or ""), source=str(item.get("source") or "indicator"), description=str(item.get("description") or "") or None, confidence=float(item.get("confidence") or 60.0), metadata=dict(item.get("metadata") or {})))
        for item in evidence:
            if item.get("indicator"):
                combined.append(self._ioc_payload(str(item["indicator"]), source="evidence", description=str(item.get("description") or "") or None, confidence=float(item.get("score") or 60.0), metadata={"evidence": True}))
        deduped: dict[str, dict[str, object]] = {}
        for item in combined:
            deduped[item["normalized_indicator"]] = item
        return sorted(deduped.values(), key=lambda item: item["confidence"], reverse=True)

    def _ioc_payload(self, indicator: str, *, source: str, description: str | None = None, confidence: float = 60.0, metadata: dict[str, object] | None = None) -> dict[str, object]:
        normalized = _normalize(indicator)
        ioc_type = _ioc_type(indicator)
        now = _now()
        return {
            "id": uuid4(),
            "indicator": indicator,
            "indicator_type": ioc_type,
            "normalized_indicator": normalized,
            "source": source,
            "description": description,
            "confidence": _clamp(confidence),
            "first_seen": now,
            "last_seen": now,
            "status": "active",
            "ioc_metadata": metadata or {},
            "created_at": now,
            "updated_at": now,
        }

    def _technique_candidates(self, tokens: set[str], request: ThreatAnalysisRequest) -> list[dict[str, object]]:
        candidates = [
            ("initial_access", "T1566", "Phishing", None, ["Email gateway", "User execution"], ["Email", "Web logs"], ["Suspicious attachment", "Unusual sender"], ["Malicious email leads to execution"], 88.0),
            ("credential_access", "T1110", "Brute Force", None, ["Account lockout"], ["Auth logs"], ["Repeated failed logins"], ["Login attempts against accounts"], 75.0),
            ("lateral_movement", "T1021", "Remote Services", None, ["Network segmentation"], ["Auth logs", "Network telemetry"], ["Remote service usage"], ["RDP/SSH pivoting"], 78.0),
            ("exfiltration", "T1041", "Exfiltration Over C2 Channel", None, ["Egress filtering"], ["Netflow"], ["High-volume beaconing"], ["Data exfiltration over channel"], 80.0),
            ("impact", "T1486", "Data Encrypted for Impact", None, ["Backups"], ["File integrity"], ["Mass file changes"], ["Ransomware encryption"], 85.0),
        ]
        mapped: list[dict[str, object]] = []
        text = " ".join([request.query, *request.mitre_tactics, *request.mitre_techniques, *request.mitre_groups, *request.atlas_techniques]).lower()
        for tactic, technique, sub_technique, group_name, mitigations, data_sources, detections, examples, confidence in candidates:
            if any(keyword in text for keyword in tactic.split("_")) or any(keyword in text for keyword in technique.lower().split("t")) or tactic in tokens:
                mapped.append(
                    {
                        "id": uuid4(),
                        "framework": "mitre_attack",
                        "tactic": tactic,
                        "technique": technique,
                        "sub_technique": sub_technique,
                        "group_name": group_name,
                        "software_name": None,
                        "mitigations": mitigations,
                        "data_sources": data_sources,
                        "detections": detections,
                        "procedure_examples": examples,
                        "version": "v15",
                        "confidence": confidence,
                        "mapping_metadata": {"source": "keyword"},
                    }
                )
        return mapped

    def _atlas_mappings(self, request: ThreatAnalysisRequest) -> list[dict[str, object]]:
        text = " ".join([request.query, *request.atlas_techniques]).lower()
        atlas_candidates = [
            ("model abuse", "LLM Attack Mapping", "Prompt Injection", 82.0),
            ("prompt", "Prompt Attack Mapping", "Prompt Leakage", 80.0),
            ("supply chain", "AI Supply Chain Mapping", "Model Tampering", 78.0),
            ("inference", "Inference Threat Mapping", "Inference Evasion", 76.0),
            ("defense", "AI Defense Mapping", "Agent Misconfiguration", 72.0),
        ]
        mappings = []
        for keyword, tactic, technique, confidence in atlas_candidates:
            if keyword in text:
                mappings.append({"id": uuid4(), "framework": "mitre_atlas", "tactic": tactic, "technique": technique, "sub_technique": None, "group_name": None, "software_name": None, "mitigations": ["Policy checks", "Input validation"], "data_sources": ["Prompt logs", "Model telemetry"], "detections": ["Unexpected prompt structure"], "procedure_examples": [f"Detected {technique.lower()}"], "version": "v1", "confidence": confidence, "mapping_metadata": {"source": "keyword"}})
        return mappings or [{"id": uuid4(), "framework": "mitre_atlas", "tactic": "AI Threat Mapping", "technique": "General AI Abuse", "sub_technique": None, "group_name": None, "software_name": None, "mitigations": ["Input validation"], "data_sources": ["AI logs"], "detections": ["Abnormal request"], "procedure_examples": ["Fallback mapping"], "version": "v1", "confidence": 65.0, "mapping_metadata": {"source": "fallback"}}]

    def _default_mapping(self, query: str) -> dict[str, object]:
        return {"id": uuid4(), "framework": "mitre_attack", "tactic": "discovery", "technique": "System Information Discovery", "sub_technique": None, "group_name": None, "software_name": None, "mitigations": ["Hardening", "Monitoring"], "data_sources": ["Endpoint logs"], "detections": ["Discovery commands"], "procedure_examples": [query], "version": "v15", "confidence": 60.0, "mapping_metadata": {"source": "fallback"}}

    def _infer_actor(self, request: ThreatAnalysisRequest, iocs: list[dict[str, object]]) -> str:
        if any("ransom" in item["indicator"].lower() for item in iocs):
            return "Ransomware Affiliate"
        if any(term in request.query.lower() for term in ("apt", "persistent", "espionage")):
            return "APT Operator"
        if any(term in request.query.lower() for term in ("phish", "credential", "account")):
            return "Credential Threat Actor"
        return request.metadata.get("attribution", "Unknown Threat Actor")

    def _actors_from_request(self, request: ThreatAnalysisRequest, iocs: list[dict[str, object]], mitre_mappings: list[dict[str, object]]) -> list[ThreatActor]:
        actor = ThreatActor(name=self._infer_actor(request, iocs), aliases=[request.metadata.get("alias", "") if request.metadata.get("alias") else ""], motivations=[request.metadata.get("motivation", "financial")], geography=[request.metadata.get("geography", "unknown")], capabilities=[mapping["technique"] for mapping in mitre_mappings[:3]], techniques=[mapping["technique"] for mapping in mitre_mappings], campaigns=[request.metadata.get("campaign", request.query[:64])], infrastructure=[ioc["indicator"] for ioc in iocs[:3]], confidence=_clamp(70.0 + len(iocs) * 5.0), actor_metadata={"source": "deterministic"})
        return [actor]

    def _campaigns_from_request(self, request: ThreatAnalysisRequest, iocs: list[dict[str, object]], mitre_mappings: list[dict[str, object]]) -> list[ThreatCampaign]:
        campaign = ThreatCampaign(name=request.metadata.get("campaign", f"Campaign-{_fingerprint(request.query)}"), aliases=[request.metadata.get("alias", "") if request.metadata.get("alias") else ""], objective=request.metadata.get("objective", request.query), impact=f"{len(iocs)} indicators mapped to {len(mitre_mappings)} techniques", techniques=[mapping["technique"] for mapping in mitre_mappings], infrastructure=[ioc["indicator"] for ioc in iocs[:3]], confidence=_clamp(65.0 + len(mitre_mappings) * 6.0), campaign_metadata={"source": "deterministic"})
        return [campaign]

    def _attack_paths(self, request: ThreatAnalysisRequest, graph_backend: GraphBackend, iocs: list[dict[str, object]]) -> list[dict[str, object]]:
        source = request.assets[0] if request.assets else request.query
        target = request.assets[-1] if request.assets else request.query
        path = graph_backend.shortest_path(_normalize(source), _normalize(target))
        if not path:
            path = [_normalize(source), _normalize(target)]
        return [
            {
                "id": uuid4(),
                "source_asset": source,
                "target_asset": target,
                "attack_chain": [{"step": index + 1, "node": node} for index, node in enumerate(path)],
                "lateral_movement": ["identity pivot", "service trust abuse"],
                "privilege_escalation": ["role abuse", "token theft"],
                "identity_compromise": request.users[:3] or [source],
                "cloud_attack_path": [asset for asset in request.assets if any(term in asset.lower() for term in ("cloud", "k8s", "container"))],
                "endpoint_attack_path": [asset for asset in request.assets if any(term in asset.lower() for term in ("endpoint", "host", "device"))],
                "data_exfiltration": [target],
                "critical_asset_exposure": [target],
                "business_impact": f"Potential impact to {target} through {len(path)} graph steps",
                "likelihood": _clamp(60.0 + len(iocs) * 4.0),
                "confidence": _clamp(65.0 + len(iocs) * 4.0),
                "attack_path_metadata": {"source": source, "target": target},
            }
        ]

    def _graph_relationships(self, request: ThreatAnalysisRequest, iocs: list[dict[str, object]], attack_paths: list[dict[str, object]], correlations: list[dict[str, object]]) -> list[dict[str, object]]:
        relationships = []
        for ioc in iocs[:10]:
            relationships.append({"source": request.query, "target": ioc["normalized_indicator"], "relation_type": "observed_ioc", "confidence": ioc["confidence"]})
        for path in attack_paths:
            relationships.append({"source": path["source_asset"], "target": path["target_asset"], "relation_type": "attack_path", "confidence": path["confidence"]})
        for correlation in correlations[:10]:
            relationships.append({"source": correlation["entity_value"], "target": ", ".join(correlation["related_entities"][:3]), "relation_type": correlation["correlation_type"], "confidence": correlation["confidence"]})
        return relationships or [{"source": request.query, "target": request.query, "relation_type": "self", "confidence": 50.0}]

    def _confidence_score(self, request: ThreatAnalysisRequest, iocs: list[dict[str, object]], evidence: list[dict[str, object]], mitre_mappings: list[dict[str, object]], correlations: list[dict[str, object]]) -> dict[str, float]:
        base = 45.0 + len(iocs) * 6.0 + len(evidence) * 3.0 + len(mitre_mappings) * 7.0 + len(correlations) * 2.0
        evidence_score = _clamp(base)
        mitre_score = _clamp(40.0 + len(mitre_mappings) * 10.0)
        graph_score = _clamp(50.0 + len(correlations) * 5.0 + len(iocs) * 2.0)
        ai_score = _clamp(60.0 + len(request.atlas_techniques) * 8.0)
        reasoning_score = _clamp(55.0 + len(request.source_references) * 3.0 + len(request.context) * 2.0)
        overall = _clamp((evidence_score * 0.25) + (mitre_score * 0.2) + (graph_score * 0.2) + (ai_score * 0.15) + (reasoning_score * 0.2))
        return {"evidence_score": evidence_score, "mitre_score": mitre_score, "graph_score": graph_score, "ai_score": ai_score, "reasoning_score": reasoning_score, "overall_confidence": overall}

    def _recommendations(self, request: ThreatAnalysisRequest, confidence: dict[str, float], kill_chain: str, iocs: list[dict[str, object]], attack_paths: list[dict[str, object]]) -> list[str]:
        recommendations = [
            f"Contain indicators associated with {kill_chain.replace('_', ' ')} activity.",
            "Harden authentication paths and monitor graph-linked infrastructure.",
            "Review MITRE mappings and update detections for the correlated techniques.",
        ]
        if attack_paths:
            recommendations.append(f"Prioritize the {attack_paths[0]['source_asset']} to {attack_paths[0]['target_asset']} attack path.")
        if confidence["overall_confidence"] < request.confidence_threshold:
            recommendations.append("Collect additional evidence to raise confidence before actioning.")
        return recommendations

    def _timeline(self, request: ThreatAnalysisRequest, iocs: list[dict[str, object]], correlations: list[dict[str, object]]) -> list[dict[str, object]]:
        now = _now()
        timeline = []
        for index, ioc in enumerate(iocs[:10], start=1):
            timeline.append({"timestamp": now - timedelta(hours=index), "event": ioc["indicator"], "type": "ioc"})
        for index, corr in enumerate(correlations[:5], start=1):
            timeline.append({"timestamp": now - timedelta(hours=index + 5), "event": corr["entity_value"], "type": "correlation"})
        return timeline

    def _risk_propagation(self, nodes: list[dict[str, object]], edges: list[dict[str, object]]) -> list[dict[str, object]]:
        propagation = []
        for edge in edges[:10]:
            propagation.append({"from": edge["source"], "to": edge["target"], "risk": _clamp(50.0 + float(edge.get("confidence", 0.0)) * 0.5)})
        return propagation

    def _entity_type(self, entity: object) -> str:
        text = str(entity).lower()
        if text.startswith("user") or "@" in text:
            return "identity"
        if any(term in text for term in ("host", "device", "endpoint")):
            return "asset"
        if any(term in text for term in ("campaign", "apt")):
            return "campaign"
        return "entity"


def build_graph_backend(nodes: list[dict[str, object]], edges: list[dict[str, object]]) -> GraphBackend:
    backend = GraphBackend()
    for node in nodes:
        backend.add_node(str(node["node_key"]), str(node.get("node_type", "entity")), str(node.get("label", node["node_key"])), **dict(node.get("properties") or {}))
    for edge in edges:
        backend.add_edge(str(edge["source"]), str(edge["target"]), str(edge.get("relation_type", "related")), float(edge.get("confidence", 50.0)), **dict(edge.get("metadata") or {}))
    return backend
