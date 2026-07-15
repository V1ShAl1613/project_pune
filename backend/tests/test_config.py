from __future__ import annotations

from app.core.settings import TestingSettings, get_settings, reset_settings_cache


def test_testing_settings_are_loaded(monkeypatch) -> None:
    monkeypatch.setenv("SENTINEL_ENVIRONMENT", "testing")
    reset_settings_cache()
    settings = get_settings()
    assert settings.environment.value == "testing"
    assert settings.database_url.startswith("postgresql+asyncpg://")
    assert settings.redis_url.startswith("redis://")


def test_testing_settings_class_has_expected_defaults() -> None:
    settings = TestingSettings()
    assert settings.debug is False
    assert settings.enable_docs is True
