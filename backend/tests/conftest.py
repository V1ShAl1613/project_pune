from __future__ import annotations

import pytest
from fastapi.testclient import TestClient

from app.core.app_factory import create_app
from app.core.settings import TestingSettings, reset_settings_cache


@pytest.fixture(autouse=True)
def _test_environment(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("SENTINEL_ENVIRONMENT", "testing")
    monkeypatch.setenv("SENTINEL_DEBUG", "false")
    reset_settings_cache()


@pytest.fixture()
def app() -> object:
    return create_app(TestingSettings())


@pytest.fixture()
def client(app) -> TestClient:
    return TestClient(app)
