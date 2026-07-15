from __future__ import annotations

from dataclasses import dataclass
from uuid import UUID

from fastapi import Request
from fastapi.testclient import TestClient

from app.auth.dependencies import provide_auth_context
from app.auth.models import AuthContext
from app.authorization.dependencies import provide_authorization_service
from app.authorization.models import AuthorizationDecision
from app.authorization import decorators as authorization_decorators
from app.core.app_factory import create_app
from app.core.settings import TestingSettings


@dataclass(slots=True)
class FakeAuthorizationService:
    allow: bool = True

    async def authorize(self, auth_context, **kwargs):
        if not self.allow or kwargs.get("permission_code") == "System.Admin":
            return AuthorizationDecision(allowed=False, reason="permission_required")
        return AuthorizationDecision(allowed=True, reason="permission_granted")

    async def list_roles(self):
        return []

    async def create_permission(self, request, actor=None):
        return type("PermissionLike", (), {"id": UUID("00000000-0000-0000-0000-000000000010"), "code": request.code, "resource": request.resource, "action": request.action, "description": request.description, "category": request.category, "created_at": __import__("datetime").datetime.now(__import__("datetime").UTC), "updated_at": __import__("datetime").datetime.now(__import__("datetime").UTC)})()


class DummySessionContext:
    async def __aenter__(self):
        return object()

    async def __aexit__(self, exc_type, exc, tb):
        return False


class DummySessionFactory:
    def __call__(self):
        return DummySessionContext()


class FakeRedis:
    async def get(self, key: str):
        return None

    async def scan_iter(self, match: str | None = None):
        if False:
            yield ""


def build_client(*, allow: bool = True, monkeypatch=None) -> TestClient:
    app = create_app(TestingSettings())
    app.state.session_factory = DummySessionFactory()
    app.state.redis_client = FakeRedis()
    fake_service = FakeAuthorizationService(allow=allow)
    if monkeypatch is not None:
        monkeypatch.setattr(authorization_decorators, "build_authorization_service", lambda session, redis, settings: fake_service)
    app.dependency_overrides[provide_auth_context] = lambda: AuthContext(
        user_id=UUID("00000000-0000-0000-0000-000000000001"),
        session_id=UUID("00000000-0000-0000-0000-000000000002"),
        access_token_jti="jti",
        refresh_token_jti=None,
        token_type="access",
    )
    app.dependency_overrides[provide_authorization_service] = lambda: fake_service

    @app.middleware("http")
    async def inject_auth_context(request: Request, call_next):
        request.state.auth_context = AuthContext(
            user_id=UUID("00000000-0000-0000-0000-000000000001"),
            session_id=UUID("00000000-0000-0000-0000-000000000002"),
            access_token_jti="jti",
            refresh_token_jti=None,
            token_type="access",
        )
        return await call_next(request)

    return TestClient(app)


def test_roles_route_allows_authorized_access(monkeypatch) -> None:
    client = build_client(monkeypatch=monkeypatch)
    response = client.get("/roles")
    assert response.status_code == 200


def test_permissions_route_denies_system_admin_without_rights(monkeypatch) -> None:
    client = build_client(allow=False, monkeypatch=monkeypatch)
    response = client.post(
        "/permissions",
        json={"code": "Test.Read", "resource": "Test", "action": "Read", "description": "test"},
    )
    assert response.status_code == 403
