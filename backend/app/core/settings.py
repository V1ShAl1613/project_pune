from __future__ import annotations

import secrets
from enum import StrEnum
from functools import lru_cache
from pathlib import Path
from typing import Any

from pydantic import Field, field_validator, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

from app.config.loader import load_environment_file


class EnvironmentName(StrEnum):
    DEVELOPMENT = "development"
    TESTING = "testing"
    PRODUCTION = "production"


def _parse_csv(value: Any) -> list[str]:
    if value is None or value == "":
        return []
    if isinstance(value, list):
        return [str(item).strip() for item in value if str(item).strip()]
    return [item.strip() for item in str(value).split(",") if item.strip()]


class AppSettings(BaseSettings):
    __test__ = False

    model_config = SettingsConfigDict(
        env_prefix="SENTINEL_",
        case_sensitive=False,
        extra="ignore",
    )

    app_name: str = "Sentinel Fusion AI"
    environment: EnvironmentName = EnvironmentName.DEVELOPMENT
    debug: bool = True
    api_v1_prefix: str = "/api/v1"
    database_url: str = "postgresql+asyncpg://localhost:5432/sentinel_fusion_ai"
    redis_url: str = "redis://localhost:6379/0"
    cors_origins: list[str] = Field(default_factory=list)
    trusted_hosts: list[str] = Field(default_factory=lambda: ["localhost", "127.0.0.1"])
    log_level: str = "INFO"
    secure_cookies: bool = True
    cookie_secure: bool = True
    cookie_http_only: bool = True
    cookie_same_site: str = "lax"
    cookie_domain: str | None = None
    cookie_path: str = "/"
    enable_docs: bool = True
    enable_redoc: bool = True
    enable_compression: bool = True
    enable_trusted_hosts: bool = True
    enable_rate_limit: bool = False
    jwt_secret_key: str | None = None
    jwt_algorithm: str = "HS256"
    jwt_issuer: str = "sentinel-fusion-ai"
    jwt_audience: str = "sentinel-fusion-ai-users"
    access_token_ttl_minutes: int = 15
    refresh_token_ttl_days: int = 7
    verification_token_ttl_minutes: int = 30
    reset_token_ttl_minutes: int = 15
    password_min_length: int = 12
    password_history_size: int = 5
    password_expiration_days: int = 90
    login_failure_threshold: int = 5
    account_lock_minutes: int = 15
    session_idle_timeout_minutes: int = 60
    session_absolute_timeout_hours: int = 24
    max_concurrent_sessions: int = 5
    max_login_delay_seconds: float = 2.0
    database_pool_size: int = 5
    database_max_overflow: int = 10
    database_pool_timeout: int = 30
    database_pool_recycle: int = 1800
    redis_max_connections: int = 20
    redis_socket_timeout: int = 5
    request_timeout_seconds: float = 30.0
    correlation_header: str = "X-Correlation-ID"
    secure_cookie_name: str = "sentinel_session"
    security_headers_policy: str = (
        "default-src 'self'; frame-ancestors 'none'; base-uri 'self'; form-action 'self'"
    )
    smtp_host: str | None = None
    smtp_port: int | None = None
    smtp_username: str | None = None
    smtp_password: str | None = None
    smtp_from_address: str | None = None
    smtp_use_tls: bool = True
    smtp_use_ssl: bool = False

    ai_gateway_enabled: bool = True
    ai_default_provider: str = "ollama"
    ai_default_model: str = "nvidia/nemotron-mini"
    ai_fallback_models: list[str] = Field(
        default_factory=lambda: ["meta/llama3", "mistral", "deepseek", "qwen", "gemma", "phi"]
    )
    ai_ollama_base_url: str = "http://localhost:11434"
    ai_ollama_timeout_seconds: float = 30.0
    ai_max_prompt_length: int = 32768
    ai_max_response_length: int = 32768
    ai_max_conversation_messages: int = 100
    ai_rate_limit_requests_per_minute: int = 60
    ai_rate_limit_window_seconds: int = 60
    ai_stream_chunk_size: int = 1024
    ai_enable_streaming: bool = True
    ai_enable_websockets: bool = True
    ai_enable_json_output: bool = True
    ai_enable_structured_output: bool = True
    ai_enable_tool_calling_placeholder: bool = True
    ai_request_signing_enabled: bool = False
    ai_security_enabled: bool = True
    ai_logging_enabled: bool = True
    ai_metrics_enabled: bool = True

    prompt_gateway_enabled: bool = True
    prompt_default_category: str = "general"
    prompt_default_template_type: str = "system"
    prompt_max_length: int = 65536
    prompt_max_variables: int = 128
    prompt_max_versions: int = 200
    prompt_max_executions_per_minute: int = 120
    prompt_cache_ttl_seconds: int = 300
    prompt_validation_cache_ttl_seconds: int = 300
    prompt_execution_cache_ttl_seconds: int = 300
    prompt_analytics_cache_ttl_seconds: int = 600
    prompt_version_cache_ttl_seconds: int = 600
    prompt_registry_cache_ttl_seconds: int = 300
    prompt_allowed_models: list[str] = Field(default_factory=lambda: ["nvidia/nemotron-mini", "meta/llama3", "mistral", "deepseek", "qwen", "gemma", "phi"])
    prompt_forbidden_keywords: list[str] = Field(
        default_factory=lambda: ["ignore previous", "bypass", "reveal secrets", "system prompt", "developer message", "jailbreak"]
    )
    prompt_sensitive_patterns: list[str] = Field(default_factory=lambda: ["api[_ -]?key", "bearer [A-Za-z0-9._-]+", "sk-[A-Za-z0-9]{16,}"])
    prompt_enable_streaming: bool = True
    prompt_enable_structured_output: bool = True
    prompt_enable_json_validation: bool = True
    prompt_enable_markdown_validation: bool = True
    prompt_enable_xml_validation: bool = True
    prompt_enable_yaml_validation: bool = True
    prompt_enable_policy_enforcement: bool = True
    prompt_enable_secret_masking: bool = True
    prompt_enable_input_sanitization: bool = True
    prompt_enable_output_sanitization: bool = True
    prompt_enable_approval_workflow: bool = True
    prompt_retention_days: int = 365
    prompt_approval_required: bool = True

    agent_gateway_enabled: bool = True
    agent_default_namespace: str = "default"
    agent_default_runtime: str = "asyncio"
    agent_default_priority: int = 50
    agent_max_name_length: int = 128
    agent_max_description_length: int = 2048
    agent_max_capabilities: int = 128
    agent_max_dependencies: int = 64
    agent_max_task_payload_bytes: int = 1024 * 1024
    agent_max_workflow_steps: int = 256
    agent_max_parallel_tasks: int = 32
    agent_task_retry_attempts: int = 3
    agent_task_timeout_seconds: float = 300.0
    agent_execution_queue_ttl_seconds: int = 3600
    agent_context_cache_ttl_seconds: int = 300
    agent_memory_cache_ttl_seconds: int = 300
    agent_metrics_cache_ttl_seconds: int = 300
    agent_health_cache_ttl_seconds: int = 60
    agent_approval_required: bool = False
    agent_audit_enabled: bool = True
    agent_security_enabled: bool = True
    agent_governance_enabled: bool = True
    agent_monitoring_enabled: bool = True
    agent_redis_queue_prefix: str = "sentinel:agents"
    agent_redis_event_prefix: str = "sentinel:agent-events"
    agent_redis_context_prefix: str = "sentinel:agent-context"
    agent_redis_execution_prefix: str = "sentinel:agent-execution"
    agent_redis_session_prefix: str = "sentinel:agent-session"

    reasoning_gateway_enabled: bool = True
    reasoning_default_strategy: str = "hybrid"
    reasoning_default_model: str = "nvidia/nemotron-mini"
    reasoning_cache_ttl_seconds: int = 300
    reasoning_evaluation_cache_ttl_seconds: int = 600
    reasoning_confidence_threshold: int = 70
    reasoning_trust_threshold: int = 70
    reasoning_risk_threshold: int = 60
    reasoning_enable_deepeval: bool = True
    reasoning_enable_ragas: bool = True
    reasoning_enable_quantum_risk: bool = True
    reasoning_enable_hallucination_detection: bool = True
    reasoning_redis_cache_prefix: str = "sentinel:reasoning"

    threat_gateway_enabled: bool = True
    threat_default_model: str = "nvidia/nemotron-mini"
    threat_cache_ttl_seconds: int = 300
    threat_redis_cache_prefix: str = "sentinel:threat"
    threat_enable_graph: bool = True
    threat_enable_mitre: bool = True
    threat_enable_ioc_correlation: bool = True
    threat_enable_attack_path: bool = True
    threat_enable_threat_hunting: bool = True
    threat_enable_qdrant: bool = True
    threat_enable_networkx: bool = True
    threat_enable_neo4j: bool = False

    banking_gateway_enabled: bool = True
    banking_default_model: str = "nvidia/nemotron-mini"
    banking_cache_ttl_seconds: int = 300
    banking_redis_cache_prefix: str = "sentinel:banking"
    banking_enable_graph: bool = True
    banking_enable_qdrant: bool = True
    banking_enable_networkx: bool = True
    banking_enable_neo4j: bool = False
    banking_enable_fraud_engine: bool = True
    banking_enable_aml_engine: bool = True
    banking_enable_ueba_engine: bool = True
    banking_enable_risk_engine: bool = True
    banking_enable_investigation_engine: bool = True
    banking_enable_device_intelligence: bool = True
    banking_enable_identity_risk: bool = True
    banking_enable_merchant_intelligence: bool = True
    banking_enable_customer_risk: bool = True
    banking_enable_reasoning_bridge: bool = True
    banking_enable_threat_bridge: bool = True
    banking_neo4j_uri: str | None = None
    banking_neo4j_user: str | None = None
    banking_neo4j_password: str | None = None
    banking_neo4j_database: str = "neo4j"
    banking_qdrant_url: str = "http://localhost:6333"
    banking_qdrant_api_key: str | None = None
    banking_qdrant_collection_prefix: str = "sentinel_banking"
    banking_qdrant_timeout_seconds: float = 30.0
    banking_qdrant_vector_size: int = 16
    banking_qdrant_distance: str = "cosine"

    grc_gateway_enabled: bool = True
    grc_cache_ttl_seconds: int = 300
    grc_redis_cache_prefix: str = "sentinel:grc"
    grc_enable_graph: bool = True
    grc_enable_qdrant: bool = True
    grc_enable_networkx: bool = True
    grc_enable_neo4j: bool = False
    grc_default_model: str = "nvidia/nemotron-mini"
    grc_qdrant_collection_prefix: str = "sentinel_grc"
    grc_neo4j_uri: str | None = None
    grc_neo4j_user: str | None = None
    grc_neo4j_password: str | None = None
    grc_neo4j_database: str = "neo4j"

    knowledge_gateway_enabled: bool = True
    knowledge_default_collection: str = "default"
    knowledge_default_owner_type: str = "organization"
    knowledge_default_security_level: str = "internal"
    knowledge_cache_ttl_seconds: int = 300
    knowledge_statistics_cache_ttl_seconds: int = 600
    knowledge_collection_cache_ttl_seconds: int = 300
    knowledge_document_cache_ttl_seconds: int = 300
    knowledge_search_cache_ttl_seconds: int = 300
    knowledge_pipeline_cache_ttl_seconds: int = 300
    knowledge_max_upload_bytes: int = 50 * 1024 * 1024
    knowledge_max_documents_per_collection: int = 100000
    knowledge_max_chunks_per_document: int = 2048
    knowledge_max_chunk_size: int = 2000
    knowledge_default_chunk_overlap: int = 200
    knowledge_default_embedding_model: str = "BAAI/bge-base-en-v1.5"
    knowledge_default_embedding_dimension: int = 768
    knowledge_embedding_batch_size: int = 32
    knowledge_embedding_retry_attempts: int = 3
    knowledge_embedding_retry_delay_seconds: float = 1.0
    knowledge_enable_hybrid_search: bool = True
    knowledge_enable_vector_search: bool = True
    knowledge_enable_keyword_search: bool = True
    knowledge_enable_metadata_search: bool = True
    knowledge_enable_ranking: bool = True
    knowledge_enable_ocr_ready: bool = True
    knowledge_enable_duplicate_detection: bool = True
    knowledge_enable_sensitive_detection: bool = True
    knowledge_enable_document_security: bool = True
    knowledge_enable_versioning: bool = True
    knowledge_enable_governance: bool = True
    knowledge_qdrant_url: str = "http://localhost:6333"
    knowledge_qdrant_api_key: str | None = None
    knowledge_qdrant_collection_prefix: str = "sentinel_knowledge"
    knowledge_qdrant_timeout_seconds: float = 30.0
    knowledge_qdrant_replicas: int = 1
    knowledge_qdrant_shards: int = 1
    knowledge_qdrant_vector_size: int = 768
    knowledge_qdrant_distance: str = "cosine"
    knowledge_qdrant_on_disk_payload: bool = True
    knowledge_qdrant_enable_snapshot: bool = False
    knowledge_allowed_file_types: list[str] = Field(
        default_factory=lambda: ["pdf", "docx", "txt", "md", "csv", "json", "xml", "html", "yaml", "yml", "log"]
    )
    knowledge_sensitive_patterns: list[str] = Field(
        default_factory=lambda: ["api[_ -]?key", "bearer [A-Za-z0-9._-]+", "sk-[A-Za-z0-9]{16,}"]
    )
    knowledge_language_detection_enabled: bool = True
    knowledge_encoding_validation_enabled: bool = True
    knowledge_virus_scan_placeholder_enabled: bool = True
    knowledge_approval_required: bool = False

    @field_validator("cors_origins", "trusted_hosts", mode="before")
    @classmethod
    def parse_lists(cls, value: Any) -> list[str]:
        return _parse_csv(value)

    @field_validator("cookie_same_site")
    @classmethod
    def validate_cookie_same_site(cls, value: str) -> str:
        normalized = value.lower()
        if normalized not in {"lax", "strict", "none"}:
            raise ValueError("cookie_same_site must be lax, strict, or none")
        return normalized

    @field_validator("database_url")
    @classmethod
    def validate_database_url(cls, value: str) -> str:
        if not value.startswith(("postgresql://", "postgresql+asyncpg://")):
            raise ValueError("database_url must use PostgreSQL")
        return value

    @field_validator("redis_url")
    @classmethod
    def validate_redis_url(cls, value: str) -> str:
        if not value.startswith(("redis://", "rediss://")):
            raise ValueError("redis_url must use Redis")
        return value

    @model_validator(mode="after")
    def apply_environment_defaults(self) -> "AppSettings":
        if not self.jwt_secret_key:
            if self.environment == EnvironmentName.PRODUCTION:
                raise ValueError("jwt_secret_key is required in production")
            self.jwt_secret_key = secrets.token_urlsafe(48)
        if self.environment == EnvironmentName.PRODUCTION:
            self.debug = False
            self.enable_docs = False
            self.enable_redoc = False
            self.enable_rate_limit = True
            self.cookie_secure = True
            self.cookie_http_only = True
            self.ai_security_enabled = True
            self.ai_metrics_enabled = True
            self.prompt_enable_policy_enforcement = True
            self.prompt_enable_secret_masking = True
            self.agent_security_enabled = True
            self.agent_governance_enabled = True
            self.agent_monitoring_enabled = True
            self.reasoning_gateway_enabled = True
            self.reasoning_enable_deepeval = True
            self.reasoning_enable_ragas = True
            self.reasoning_enable_quantum_risk = True
            self.reasoning_enable_hallucination_detection = True
            self.threat_gateway_enabled = True
            self.threat_enable_graph = True
            self.threat_enable_mitre = True
            self.threat_enable_ioc_correlation = True
            self.threat_enable_attack_path = True
            self.threat_enable_threat_hunting = True
            self.banking_gateway_enabled = True
            self.banking_enable_graph = True
            self.banking_enable_fraud_engine = True
            self.banking_enable_aml_engine = True
            self.banking_enable_ueba_engine = True
            self.banking_enable_risk_engine = True
            self.banking_enable_investigation_engine = True
            self.knowledge_enable_governance = True
            self.knowledge_enable_document_security = True
        return self


class DevelopmentSettings(AppSettings):
    __test__ = False

    environment: EnvironmentName = EnvironmentName.DEVELOPMENT
    debug: bool = True
    log_level: str = "DEBUG"


class TestingSettings(AppSettings):
    __test__ = False

    environment: EnvironmentName = EnvironmentName.TESTING
    debug: bool = False
    database_url: str = "postgresql+asyncpg://localhost:5432/sentinel_fusion_ai_test"
    redis_url: str = "redis://localhost:6379/1"
    trusted_hosts: list[str] = Field(default_factory=lambda: ["localhost", "127.0.0.1", "testserver"])


class ProductionSettings(AppSettings):
    __test__ = False

    environment: EnvironmentName = EnvironmentName.PRODUCTION
    debug: bool = False
    enable_docs: bool = False
    enable_redoc: bool = False
    enable_rate_limit: bool = True
    trusted_hosts: list[str] = Field(default_factory=list)


def _resolve_settings_class(environment: EnvironmentName) -> type[AppSettings]:
    if environment == EnvironmentName.TESTING:
        return TestingSettings
    if environment == EnvironmentName.PRODUCTION:
        return ProductionSettings
    return DevelopmentSettings


@lru_cache(maxsize=1)
def get_settings() -> AppSettings:
    load_environment_file(Path(__file__).resolve().parents[2])
    environment = EnvironmentName(
        __import__("os").environ.get("SENTINEL_ENVIRONMENT", "development").lower()
    )
    settings_cls = _resolve_settings_class(environment)
    return settings_cls()


def reset_settings_cache() -> None:
    get_settings.cache_clear()
