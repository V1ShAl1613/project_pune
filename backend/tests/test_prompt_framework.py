from __future__ import annotations

from app.prompt.dependencies import provide_prompt_service


class _FakePromptService:
    async def list_categories(self):
        return []


def test_prompt_categories_route_is_registered(client, app) -> None:
    app.dependency_overrides[provide_prompt_service] = lambda: _FakePromptService()
    try:
        response = client.get("/prompts/categories")
    finally:
        app.dependency_overrides.clear()

    assert response.status_code == 200
    assert response.json() == []
