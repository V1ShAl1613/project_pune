from __future__ import annotations

from app.database import health as health_module


def test_root_endpoint(client) -> None:
    response = client.get("/")
    assert response.status_code == 200
    assert response.json()["status"] == "running"


def test_health_endpoint(client) -> None:
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"


def test_ready_endpoint_returns_structured_json(client, monkeypatch) -> None:
    async def healthy_db(*args, **kwargs):
        return {"status": "healthy", "message": "database connection available", "latency_ms": 1.0}

    async def healthy_redis(*args, **kwargs):
        return {"status": "healthy", "message": "redis connection available", "latency_ms": 1.0}

    monkeypatch.setattr(health_module, "check_database_health", healthy_db)
    monkeypatch.setattr(health_module, "check_redis_health", healthy_redis)
    response = client.get("/ready")
    assert response.status_code == 200
    payload = response.json()
    assert payload["status"] == "ready"
    assert payload["checks"]["database"]["status"] == "healthy"


def test_metrics_endpoint_returns_structured_json(client) -> None:
    response = client.get("/metrics")
    assert response.status_code == 200
    payload = response.json()
    assert payload["status"] == "ok"
    assert "requests" in payload
