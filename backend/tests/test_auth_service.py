from __future__ import annotations

from contextlib import asynccontextmanager
from dataclasses import dataclass
from datetime import UTC, datetime
from uuid import uuid4
from uuid import UUID

import pytest

from app.auth.emails.smtp import SmtpEmailClient
from app.auth.models import AuthRequestContext
from app.auth.repositories.auth_repository import AuthRepository
from app.auth.security.password_hasher import PasswordHasher
from app.auth.services.auth_service import AuthService
from app.auth.tokens.generator import TokenGenerator
from app.auth.tokens.repository import TokenRepository
from app.auth.tokens.service import JwtService
from app.auth.tokens.validator import TokenValidator
from app.auth.schemas.auth import ForgotPasswordRequest, LoginRequest, LogoutRequest, RegisterRequest, RefreshRequest, ResetPasswordRequest
from app.core.settings import TestingSettings
from app.database.models import AuditLog
from app.database.models.identity import RefreshToken, Session as AuthSession, User


@dataclass(slots=True)
class FakeEmailClient:
    settings: TestingSettings
    sent_messages: list[tuple[str, str]]

    def send(self, recipient_email: str, template) -> bool:
        self.sent_messages.append((recipient_email, template.body))
        return True


class FakeTokenRepository:
    def __init__(self) -> None:
        self.refresh_tokens: dict[str, dict[str, object]] = {}
        self.revoked_refresh_tokens: set[str] = set()
        self.sessions: dict[str, dict[str, object]] = {}
        self.revoked_sessions: set[str] = set()
        self.failed_logins: dict[str, int] = {}
        self.locked_accounts: set[str] = set()
        self.one_time_tokens: dict[tuple[str, str], dict[str, object]] = {}

    async def store_refresh_token(self, token_hash: str, payload: dict[str, object], ttl_seconds: int) -> None:
        self.refresh_tokens[token_hash] = payload

    async def get_refresh_token(self, token_hash: str) -> dict[str, object] | None:
        return self.refresh_tokens.get(token_hash)

    async def revoke_refresh_token(self, token_hash: str, ttl_seconds: int) -> None:
        self.revoked_refresh_tokens.add(token_hash)

    async def is_refresh_token_revoked(self, token_hash: str) -> bool:
        return token_hash in self.revoked_refresh_tokens

    async def store_session(self, session_id: str, payload: dict[str, object], ttl_seconds: int) -> None:
        self.sessions[session_id] = payload

    async def get_session(self, session_id: str) -> dict[str, object] | None:
        return self.sessions.get(session_id)

    async def revoke_session(self, session_id: str, ttl_seconds: int) -> None:
        self.revoked_sessions.add(session_id)

    async def is_session_revoked(self, session_id: str) -> bool:
        return session_id in self.revoked_sessions

    async def increment_failed_login(self, identifier: str, ttl_seconds: int) -> int:
        self.failed_logins[identifier] = self.failed_logins.get(identifier, 0) + 1
        return self.failed_logins[identifier]

    async def reset_failed_login(self, identifier: str) -> None:
        self.failed_logins.pop(identifier, None)
        self.locked_accounts.discard(identifier)

    async def get_failed_login_count(self, identifier: str) -> int:
        return self.failed_logins.get(identifier, 0)

    async def lock_account(self, identifier: str, ttl_seconds: int) -> None:
        self.locked_accounts.add(identifier)

    async def is_account_locked(self, identifier: str) -> bool:
        return identifier in self.locked_accounts

    async def store_one_time_token(self, kind: str, token_hash: str, payload: dict[str, object], ttl_seconds: int) -> None:
        self.one_time_tokens[(kind, token_hash)] = payload

    async def consume_one_time_token(self, kind: str, token_hash: str) -> dict[str, object] | None:
        return self.one_time_tokens.pop((kind, token_hash), None)


class FakeAuthRepository:
    def __init__(self) -> None:
        self.users: dict[str, User] = {}
        self.users_by_id: dict[object, User] = {}
        self.sessions: dict[object, AuthSession] = {}
        self.refresh_tokens: dict[str, RefreshToken] = {}
        self.audit_logs: list[AuditLog] = []

    @asynccontextmanager
    async def transaction(self):
        yield self

    async def find_user_by_email(self, email: str):
        return self.users.get(email)

    async def find_user_by_identifier(self, identifier: str):
        return self.users.get(identifier)

    async def find_user_by_id(self, user_id):
        if isinstance(user_id, str):
            try:
                user_id = UUID(user_id)
            except ValueError:
                return None
        return self.users_by_id.get(user_id)

    async def create_user(self, user: User):
        if getattr(user, "id", None) is None:
            user.id = uuid4()
        self.users[user.email] = user
        self.users[user.username] = user
        self.users_by_id[user.id] = user
        return user

    async def update_user(self, user: User, values: dict[str, object]):
        for key, value in values.items():
            setattr(user, key, value)
        return user

    async def create_session(self, session: AuthSession):
        if getattr(session, "id", None) is None:
            session.id = uuid4()
        self.sessions[session.id] = session
        return session

    async def update_session(self, session: AuthSession, values: dict[str, object]):
        for key, value in values.items():
            setattr(session, key, value)
        return session

    async def create_refresh_token(self, refresh_token: RefreshToken):
        if getattr(refresh_token, "id", None) is None:
            refresh_token.id = uuid4()
        self.refresh_tokens[refresh_token.jti] = refresh_token
        return refresh_token

    async def update_refresh_token(self, refresh_token: RefreshToken, values: dict[str, object]):
        for key, value in values.items():
            setattr(refresh_token, key, value)
        return refresh_token

    async def get_session_by_id(self, session_id):
        return self.sessions.get(session_id)

    async def get_refresh_token_by_jti(self, jti: str):
        return self.refresh_tokens.get(jti)

    async def get_refresh_token_by_hash(self, token_hash: str):
        for refresh_token in self.refresh_tokens.values():
            if refresh_token.token_hash == token_hash:
                return refresh_token
        return None

    async def list_active_sessions(self, user_id):
        return [session for session in self.sessions.values() if session.user_id == user_id and session.status == "active"]

    async def revoke_session(self, session: AuthSession, reason: str = "logout"):
        session.status = "revoked"
        return session

    async def revoke_refresh_token(self, refresh_token: RefreshToken, reason: str = "logout"):
        refresh_token.status = "revoked"
        return refresh_token

    async def create_audit_log(self, audit_log: AuditLog):
        self.audit_logs.append(audit_log)
        return audit_log


@pytest.fixture()
def auth_service() -> AuthService:
    settings = TestingSettings()
    jwt_service = JwtService(settings)
    return AuthService(
        repository=FakeAuthRepository(),
        settings=settings,
        jwt_service=jwt_service,
        token_generator=TokenGenerator(settings, jwt_service),
        token_validator=TokenValidator(jwt_service),
        token_repository=FakeTokenRepository(),
        password_hasher=PasswordHasher(),
        email_client=FakeEmailClient(settings=settings, sent_messages=[]),
        logger=__import__("logging").getLogger("test.auth"),
        audit_logger=__import__("logging").getLogger("test.audit"),
    )


@pytest.mark.asyncio
async def test_register_login_refresh_logout_and_reset(auth_service: AuthService) -> None:
    context = AuthRequestContext(ip_address="127.0.0.1", user_agent="pytest", device_id="device-1", device_name="Laptop")

    registration = await auth_service.register(
        RegisterRequest(
            email="alice@example.com",
            username="alice",
            display_name="Alice Example",
            password="Str0ng!Password",
            phone_number="+1234567890",
        ),
        context,
    )
    assert registration.user.email == "alice@example.com"

    login = await auth_service.login(LoginRequest(identifier="alice@example.com", password="Str0ng!Password", device_name="Laptop"), context)
    assert login.tokens.access_token
    assert login.tokens.refresh_token

    refreshed = await auth_service.refresh(RefreshRequest(refresh_token=login.tokens.refresh_token), context)
    assert refreshed.tokens.access_token != login.tokens.access_token

    logout = await auth_service.logout(LogoutRequest(refresh_token=refreshed.tokens.refresh_token), context=context)
    assert logout.message == "Logout successful"


@pytest.mark.asyncio
async def test_forgot_and_reset_password_flow(auth_service: AuthService) -> None:
    context = AuthRequestContext(ip_address="127.0.0.1", user_agent="pytest")
    await auth_service.register(
        RegisterRequest(
            email="bob@example.com",
            username="bob",
            display_name="Bob Example",
            password="Str0ng!Password",
        ),
        context,
    )
    await auth_service.forgot_password(ForgotPasswordRequest(email="bob@example.com"), context)
    email_client = auth_service.email_client
    token = email_client.sent_messages[-1][1].splitlines()[-1]
    result = await auth_service.reset_password(ResetPasswordRequest(token=token, new_password="N3w!Password123"), context)
    assert result.message == "Password reset successful"
