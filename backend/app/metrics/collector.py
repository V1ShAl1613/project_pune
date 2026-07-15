from __future__ import annotations

import threading
from dataclasses import dataclass, field
from datetime import datetime, timezone

try:
    from prometheus_client import Counter, Gauge, Histogram
except ModuleNotFoundError:  # pragma: no cover - fallback for lean test environments
    class _Metric:
        def __init__(self, *args, **kwargs) -> None:
            self._value = 0.0

        def labels(self, *args, **kwargs):
            return self

        def inc(self, amount: float = 1.0) -> None:
            self._value += amount

        def observe(self, amount: float) -> None:
            self._value += amount

        def set(self, value: float) -> None:
            self._value = value

    def Counter(*args, **kwargs):
        return _Metric()

    def Gauge(*args, **kwargs):
        return _Metric()

    def Histogram(*args, **kwargs):
        return _Metric()


REQUEST_COUNTER = Counter("sentinel_requests_total", "Total HTTP requests handled", ["method", "path", "status"])
REQUEST_LATENCY = Histogram("sentinel_request_duration_seconds", "HTTP request latency in seconds", ["method", "path"])
ACTIVE_REQUESTS = Gauge("sentinel_active_requests", "Current in-flight HTTP requests")


@dataclass(slots=True)
class MetricsCollector:
    started_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    total_requests: int = 0
    total_errors: int = 0
    total_latency_ms: float = 0.0
    active_requests: int = 0
    _lock: threading.Lock = field(default_factory=threading.Lock)

    def record_request(self, method: str, path: str, status_code: int, duration_ms: float) -> None:
        with self._lock:
            self.total_requests += 1
            self.total_latency_ms += duration_ms
            if status_code >= 400:
                self.total_errors += 1
            self.active_requests = max(0, self.active_requests)
        REQUEST_COUNTER.labels(method=method, path=path, status=str(status_code)).inc()
        REQUEST_LATENCY.labels(method=method, path=path).observe(duration_ms / 1000.0)
        ACTIVE_REQUESTS.set(self.active_requests)

    def snapshot(self) -> dict[str, object]:
        with self._lock:
            average_latency = self.total_latency_ms / self.total_requests if self.total_requests else 0.0
            uptime_seconds = (datetime.now(timezone.utc) - self.started_at).total_seconds()
            return {
                "status": "ok",
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "uptime_seconds": round(uptime_seconds, 2),
                "requests": {
                    "total": self.total_requests,
                    "errors": self.total_errors,
                    "active": self.active_requests,
                    "average_latency_ms": round(average_latency, 2),
                },
            }


metrics_collector = MetricsCollector()
