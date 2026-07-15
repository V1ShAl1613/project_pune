from __future__ import annotations

from contextlib import asynccontextmanager
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any, AsyncIterator

from sqlalchemy import func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.models import AuditLog
from app.database.models.identity import RefreshToken, Session as AuthSession, User
from app.database.repositories.base import CRUDRepository


@dataclass(slots=True)
class AuthRepository:
    session: AsyncSession

    @asynccontextmanager
    async def transaction(self) -> AsyncIterator[AsyncSession]:
        async with self.session.begin():
            yield self.session

    async def find_user_by_identifier(self, identifier: str) -> User | None:
        normalized = identifier.strip().lower()
        statement = select(User).where(or_(func.lower(User.email) == normalized, func.lower(User.username) == normalized))
        result = await self.session.execute(statement)
        return result.scalar_one_or_none()

    async def find_user_by_email(self, email: str) -> User | None:
        statement = select(User).where(func.lower(User.email) == email.strip().lower())
        result = await self.session.execute(statement)
        return result.scalar_one_or_none()

    async def find_user_by_id(self, user_id) -> User | None:
        return await self.session.get(User, user_id)

    async def create_user(self, user: User) -> User:
        self.session.add(user)
        await self.session.flush()
        return user

    async def update_user(self, user: User, values: dict[str, Any]) -> User:
        for key, value in values.items():
            if hasattr(user, key):
                setattr(user, key, value)
        await self.session.flush()
        return user

    async def create_session(self, session: AuthSession) -> AuthSession:
        self.session.add(session)
        await self.session.flush()
        return session

    async def update_session(self, session: AuthSession, values: dict[str, Any]) -> AuthSession:
        for key, value in values.items():
            if hasattr(session, key):
                setattr(session, key, value)
        await self.session.flush()
        return session

    async def create_refresh_token(self, refresh_token: RefreshToken) -> RefreshToken:
        self.session.add(refresh_token)
        await self.session.flush()
        return refresh_token

    async def update_refresh_token(self, refresh_token: RefreshToken, values: dict[str, Any]) -> RefreshToken:
        for key, value in values.items():
            if hasattr(refresh_token, key):
                setattr(refresh_token, key, value)
        await self.session.flush()
        return refresh_token

    async def get_session_by_id(self, session_id) -> AuthSession | None:
        return await self.session.get(AuthSession, session_id)

    async def get_refresh_token_by_jti(self, jti: str) -> RefreshToken | None:
        result = await self.session.execute(select(RefreshToken).where(RefreshToken.jti == jti))
        return result.scalar_one_or_none()

    async def get_refresh_token_by_hash(self, token_hash: str) -> RefreshToken | None:
        result = await self.session.execute(select(RefreshToken).where(RefreshToken.token_hash == token_hash))
        return result.scalar_one_or_none()

    async def list_active_sessions(self, user_id) -> list[AuthSession]:
        result = await self.session.execute(
            select(AuthSession).where(AuthSession.user_id == user_id, AuthSession.status == "active")
            .order_by(AuthSession.last_activity_at.desc().nullslast(), AuthSession.created_at.desc())
        )
        return list(result.scalars().all())

    async def revoke_session(self, session: AuthSession, reason: str = "logout") -> AuthSession:
        session.status = "revoked"
        session.session_metadata = {**(session.session_metadata or {}), "revoked_reason": reason}
        await self.session.flush()
        return session

    async def revoke_refresh_token(self, refresh_token: RefreshToken, reason: str = "logout") -> RefreshToken:
        refresh_token.status = "revoked"
        refresh_token.revoked_at = datetime.now(timezone.utc)
        refresh_token.revoked_reason = reason
        await self.session.flush()
        return refresh_token

    async def create_audit_log(self, audit_log: AuditLog) -> AuditLog:
        self.session.add(audit_log)
        await self.session.flush()
        return audit_log
