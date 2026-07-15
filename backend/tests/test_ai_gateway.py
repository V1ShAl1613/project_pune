from __future__ import annotations

from app.ai.dependencies import provide_ai_service


class _FakeAIService:
    async def health(self):
        return {
            "status": "healthy",
            "providers": [],
            "models": [],
            "metrics": {"enabled": True},
        }


def test_ai_health_endpoint_is_registered(client, app) -> None:
    app.dependency_overrides[provide_ai_service] = lambda: _FakeAIService()
    try:
        response = client.get("/ai/health")
    finally:
        app.dependency_overrides.clear()

    assert response.status_code == 200
    payload = response.json()
    assert payload["status"] == "healthy"
    assert payload["providers"] == []
