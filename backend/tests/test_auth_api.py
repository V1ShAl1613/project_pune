from __future__ import annotations

from dataclasses import dataclass
from uuid import UUID

from fastapi.testclient import TestClient

from app.auth.dependencies import provide_auth_context, provide_auth_service
from app.auth.models import AuthContext
from app.auth.schemas.auth import (
    AuthSessionResponse,
    AuthTokensResponse,
    AuthUserResponse,
    LoginResponse,
    MessageResponse,
    ProfileResponse,
    RegistrationResponse,
    SessionResponse,
)
from app.core.app_factory import create_app
from app.core.settings import TestingSettings


@dataclass(slots=True)
class ApiFakeAuthService:
    async def register(self, request, context=None):
        user = AuthUserResponse(
            id="00000000-0000-0000-0000-000000000001",
            email=request.email,
            username=request.username,
            display_name=request.display_name,
            phone_number=request.phone_number,
            status="active",
            email_verified_at=None,
            last_login_at=None,
        )
        return RegistrationResponse(user=user, verification_email_sent=True, message="Registration successful")

    async def login(self, request, context=None):
        user = AuthUserResponse(
            id="00000000-0000-0000-0000-000000000001",
            email="alice@example.com",
            username="alice",
            display_name="Alice Example",
            phone_number=None,
            status="active",
            email_verified_at=None,
            last_login_at=None,
        )
        session = AuthSessionResponse(
            id="00000000-0000-0000-0000-000000000002",
            status="active",
            session_token="session-token",
            expires_at="2026-07-14T00:00:00Z",
            last_seen_at=None,
            last_activity_at=None,
            ip_address=None,
            user_agent=None,
            device_id=None,
            device_name=None,
        )
        tokens = AuthTokensResponse(access_token="access", refresh_token="refresh", access_expires_in=900, refresh_expires_in=604800)
        return LoginResponse(user=user, session=session, tokens=tokens, message="Login successful")

    async def get_profile(self, auth_context):
        user = AuthUserResponse(
            id="00000000-0000-0000-0000-000000000001",
            email="alice@example.com",
            username="alice",
            display_name="Alice Example",
            phone_number=None,
            status="active",
            email_verified_at=None,
            last_login_at=None,
        )
        return ProfileResponse(user=user)

    async def get_session(self, auth_context):
        session = AuthSessionResponse(
            id="00000000-0000-0000-0000-000000000002",
            status="active",
            session_token="session-token",
            expires_at="2026-07-14T00:00:00Z",
            last_seen_at=None,
            last_activity_at=None,
            ip_address=None,
            user_agent=None,
            device_id=None,
            device_name=None,
        )
        return SessionResponse(session=session)

    async def logout(self, request, auth_context=None, context=None):
        return MessageResponse(message="Logout successful")

    async def refresh(self, request, context=None):
        return await self.login(request)

    async def forgot_password(self, request, context=None):
        return MessageResponse(message="If the account exists, a reset email has been sent")

    async def reset_password(self, request, context=None):
        return MessageResponse(message="Password reset successful")

    async def revoke_current_session(self, auth_context, context=None):
        return MessageResponse(message="Session revoked")


def build_client() -> TestClient:
    app = create_app(TestingSettings())
    app.dependency_overrides[provide_auth_service] = lambda: ApiFakeAuthService()
    app.dependency_overrides[provide_auth_context] = lambda: AuthContext(
        user_id=UUID("00000000-0000-0000-0000-000000000001"),
        session_id=UUID("00000000-0000-0000-0000-000000000002"),
        access_token_jti="jti",
        refresh_token_jti="refresh-jti",
        token_type="access",
    )
    return TestClient(app)


def test_auth_register_and_profile_routes() -> None:
    client = build_client()
    register = client.post(
        "/auth/register",
        json={
            "email": "alice@example.com",
            "username": "alice",
            "display_name": "Alice Example",
            "password": "Str0ng!Password",
            "phone_number": "+1234567890",
        },
    )
    assert register.status_code == 200
    profile = client.get(
        "/auth/profile",
        headers={"Authorization": "Bearer access"},
    )
    assert profile.status_code == 200
