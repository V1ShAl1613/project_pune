from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class ErrorResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    error_code: str
    message: str
    details: dict[str, object] = Field(default_factory=dict)


class ServiceHealthResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    status: str
    service: str
    environment: str


class ReadinessCheckResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    status: str
    service: str
    environment: str
    checks: dict[str, object]


class MetricsResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    status: str
    timestamp: datetime
    uptime_seconds: float
    requests: dict[str, object]
