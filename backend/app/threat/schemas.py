from __future__ import annotations

from datetime import datetime
from enum import StrEnum
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, field_validator


class IOCType(StrEnum):
    IP = "ip"
    URL = "url"
    DOMAIN = "domain"
    HASH = "hash"
    EMAIL = "email"
    CERTIFICATE = "certificate"
    REGISTRY = "registry"
    MUTEX = "mutex"
    PROCESS = "process"
    FILE = "file"
    CLOUD_RESOURCE = "cloud_resource"
    CONTAINER = "container"
    KUBERNETES_OBJECT = "kubernetes_object"
    IDENTITY = "identity"
    API_KEY = "api_key"


class ThreatHuntType(StrEnum):
    IOC = "ioc"
    BEHAVIOR = "behavior"
    MITRE = "mitre"
    IDENTITY = "identity"
    CLOUD = "cloud"
    ENDPOINT = "endpoint"
    NETWORK = "network"
    CUSTOM = "custom"


class GraphQueryType(StrEnum):
    TRAVERSAL = "traversal"
    SHORTEST_PATH = "shortest_path"
    ATTACK_PATH = "attack_path"
    RELATIONSHIP = "relationship"
    RISK_PROPAGATION = "risk_propagation"
    CENTRALITY = "centrality"
    COMMUNITY = "community"
    INFLUENCE = "influence"


class ThreatAnalysisRequest(BaseModel):
    model_config = ConfigDict(extra="forbid", protected_namespaces=())

    query: str = Field(min_length=1, max_length=8192)
    context: dict[str, object] = Field(default_factory=dict)
    iocs: list[str] = Field(default_factory=list)
    indicators: list[dict[str, object]] = Field(default_factory=list)
    assets: list[str] = Field(default_factory=list)
    users: list[str] = Field(default_factory=list)
    organizations: list[str] = Field(default_factory=list)
    source_references: list[str] = Field(default_factory=list)
    mitre_tactics: list[str] = Field(default_factory=list)
    mitre_techniques: list[str] = Field(default_factory=list)
    mitre_groups: list[str] = Field(default_factory=list)
    atlas_techniques: list[str] = Field(default_factory=list)
    events: list[dict[str, object]] = Field(default_factory=list)
    business_context: str | None = None
    technical_context: str | None = None
    confidence_threshold: int = Field(default=70, ge=0, le=100)
    metadata: dict[str, object] = Field(default_factory=dict)

    @field_validator("iocs", "source_references", "mitre_tactics", "mitre_techniques", "mitre_groups", "atlas_techniques", "assets", "users", "organizations")
    @classmethod
    def _trim_lists(cls, value: list[str]) -> list[str]:
        return [item.strip() for item in value if item and item.strip()]


class ThreatCorrelateRequest(ThreatAnalysisRequest):
    alerts: list[dict[str, object]] = Field(default_factory=list)
    incidents: list[dict[str, object]] = Field(default_factory=list)
    cases: list[dict[str, object]] = Field(default_factory=list)
    historical_events: list[dict[str, object]] = Field(default_factory=list)
    policies: list[str] = Field(default_factory=list)


class ThreatHuntRequest(ThreatAnalysisRequest):
    hunt_type: ThreatHuntType = ThreatHuntType.CUSTOM
    scheduled: bool = False
    schedule_cron: str | None = None
    lookback_hours: int = Field(default=72, ge=1, le=24 * 365)
    limit: int = Field(default=25, ge=1, le=200)


class AttackPathAnalyzeRequest(BaseModel):
    model_config = ConfigDict(extra="forbid", protected_namespaces=())

    source_asset: str = Field(min_length=1, max_length=255)
    target_asset: str = Field(min_length=1, max_length=255)
    iocs: list[str] = Field(default_factory=list)
    identities: list[str] = Field(default_factory=list)
    assets: list[str] = Field(default_factory=list)
    context: dict[str, object] = Field(default_factory=dict)
    metadata: dict[str, object] = Field(default_factory=dict)


class GraphQueryRequest(BaseModel):
    model_config = ConfigDict(extra="forbid", protected_namespaces=())

    query: str = Field(min_length=1, max_length=8192)
    query_type: GraphQueryType = GraphQueryType.TRAVERSAL
    source: str | None = None
    target: str | None = None
    limit: int = Field(default=20, ge=1, le=200)
    filters: dict[str, object] = Field(default_factory=dict)
    context: dict[str, object] = Field(default_factory=dict)


class GraphPathRequest(BaseModel):
    model_config = ConfigDict(extra="forbid", protected_namespaces=())

    source: str = Field(min_length=1, max_length=255)
    target: str = Field(min_length=1, max_length=255)
    relation_type: str | None = None


class IOCSearchRequest(BaseModel):
    model_config = ConfigDict(extra="forbid", protected_namespaces=())

    query: str
    indicator_type: IOCType | None = None
    limit: int = Field(default=25, ge=1, le=200)
    confidence_threshold: int = Field(default=50, ge=0, le=100)
    enrich: bool = True
    deduplicate: bool = True
    context: dict[str, object] = Field(default_factory=dict)


class IOCResponse(BaseModel):
    model_config = ConfigDict(extra="forbid", from_attributes=True, protected_namespaces=())

    id: UUID
    indicator: str
    indicator_type: str
    normalized_indicator: str
    source: str
    description: str | None
    confidence: float
    first_seen: datetime | None
    last_seen: datetime | None
    status: str
    ioc_metadata: dict[str, object]
    created_at: datetime
    updated_at: datetime


class ThreatActorResponse(BaseModel):
    model_config = ConfigDict(extra="forbid", from_attributes=True, protected_namespaces=())

    id: UUID
    name: str
    aliases: list[str]
    motivations: list[str]
    geography: list[str]
    capabilities: list[str]
    techniques: list[str]
    campaigns: list[str]
    infrastructure: list[str]
    confidence: float
    actor_metadata: dict[str, object]
    created_at: datetime
    updated_at: datetime


class ThreatCampaignResponse(BaseModel):
    model_config = ConfigDict(extra="forbid", from_attributes=True, protected_namespaces=())

    id: UUID
    name: str
    aliases: list[str]
    objective: str
    impact: str
    techniques: list[str]
    infrastructure: list[str]
    confidence: float
    campaign_metadata: dict[str, object]
    created_at: datetime
    updated_at: datetime


class MITREMappingResponse(BaseModel):
    model_config = ConfigDict(extra="forbid", from_attributes=True, protected_namespaces=())

    id: UUID
    framework: str
    tactic: str
    technique: str
    sub_technique: str | None
    group_name: str | None
    software_name: str | None
    mitigations: list[str]
    data_sources: list[str]
    detections: list[str]
    procedure_examples: list[str]
    version: str
    confidence: float
    mapping_metadata: dict[str, object]
    created_at: datetime
    updated_at: datetime


class ThreatCorrelationResponse(BaseModel):
    model_config = ConfigDict(extra="forbid", from_attributes=True, protected_namespaces=())

    id: UUID
    correlation_type: str
    entity_type: str
    entity_value: str
    confidence: float
    evidence_count: int
    related_entities: list[str]
    timeline: list[dict[str, object]]
    attribution: str | None
    correlation_metadata: dict[str, object]
    created_at: datetime
    updated_at: datetime


class ThreatHuntResponse(BaseModel):
    model_config = ConfigDict(extra="forbid", from_attributes=True, protected_namespaces=())

    id: UUID
    hunt_type: str
    query: str
    status: str
    confidence: float
    findings: list[dict[str, object]]
    mitre_mappings: list[MITREMappingResponse]
    iocs: list[IOCResponse]
    graph_relationships: list[dict[str, object]]
    recommendations: list[str]
    business_impact: str
    hunt_metadata: dict[str, object]
    created_at: datetime
    updated_at: datetime


class AttackPathResponse(BaseModel):
    model_config = ConfigDict(extra="forbid", from_attributes=True, protected_namespaces=())

    id: UUID
    source_asset: str
    target_asset: str
    attack_chain: list[dict[str, object]]
    lateral_movement: list[str]
    privilege_escalation: list[str]
    identity_compromise: list[str]
    cloud_attack_path: list[str]
    endpoint_attack_path: list[str]
    data_exfiltration: list[str]
    critical_asset_exposure: list[str]
    business_impact: str
    likelihood: float
    confidence: float
    attack_path_metadata: dict[str, object]
    created_at: datetime
    updated_at: datetime


class GraphNodeResponse(BaseModel):
    model_config = ConfigDict(extra="forbid", from_attributes=True, protected_namespaces=())

    id: UUID
    node_type: str
    node_key: str
    label: str
    properties: dict[str, object]
    confidence: float
    created_at: datetime
    updated_at: datetime


class GraphEdgeResponse(BaseModel):
    model_config = ConfigDict(extra="forbid", from_attributes=True, protected_namespaces=())

    id: UUID
    source_node_key: str
    target_node_key: str
    relation_type: str
    confidence: float
    edge_metadata: dict[str, object]
    created_at: datetime
    updated_at: datetime


class GraphQueryResponse(BaseModel):
    model_config = ConfigDict(extra="forbid", protected_namespaces=())

    query: str
    query_type: str
    nodes: list[dict[str, object]]
    edges: list[dict[str, object]]
    shortest_path: list[str]
    centrality: dict[str, float]
    communities: list[list[str]]
    risk_propagation: list[dict[str, object]]
    influence: dict[str, float]
    metadata: dict[str, object]


class MITREMatrixResponse(BaseModel):
    model_config = ConfigDict(extra="forbid", protected_namespaces=())

    tactics: list[str]
    techniques: list[dict[str, object]]
    groups: list[str]
    software: list[str]
    mitigations: list[str]
    data_sources: list[str]
    detections: list[str]
    version: str
    confidence: float


class ThreatAnalysisResponse(BaseModel):
    model_config = ConfigDict(extra="forbid", from_attributes=True, protected_namespaces=())

    id: UUID
    query: str
    evidence: list[dict[str, object]]
    mitre_mappings: list[MITREMappingResponse]
    mitre_atlas_mappings: list[MITREMappingResponse]
    kill_chain_stage: str
    diamond_model: dict[str, object]
    graph_relationships: list[dict[str, object]]
    attack_paths: list[AttackPathResponse]
    correlations: list[ThreatCorrelationResponse]
    iocs: list[IOCResponse]
    threat_actors: list[ThreatActorResponse]
    campaigns: list[ThreatCampaignResponse]
    confidence: float
    confidence_breakdown: dict[str, float]
    recommendations: list[str]
    business_impact: str
    technical_impact: str
    timeline: list[dict[str, object]]
    explainability: dict[str, object]
    metadata: dict[str, object]
    created_at: datetime
    updated_at: datetime


class ThreatMetricsResponse(BaseModel):
    model_config = ConfigDict(extra="forbid", protected_namespaces=())

    total_threats: int
    total_iocs: int
    total_correlations: int
    total_hunts: int
    total_attack_paths: int
    mitre_coverage: float
    detection_accuracy: float
    confidence_average: float
    risk_trend: float
    correlation_rate: float
    hunt_success_rate: float
    graph_health: dict[str, object]
    scorecard: dict[str, float]
