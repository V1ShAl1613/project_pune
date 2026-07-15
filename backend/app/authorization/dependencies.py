from __future__ import annotations

from typing import AsyncIterator

from fastapi import Depends, Request
from redis.asyncio import Redis
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.dependencies import provide_optional_auth_context, provide_auth_context
from app.auth.models import AuthContext
from app.authorization.models import AuthorizationContext
from app.authorization.permissions.engine import PermissionEngine
from app.authorization.policies.engine import PolicyEngine
from app.authorization.repositories.cache_repository import AuthorizationCacheRepository
from app.authorization.repositories.permission_repository import PermissionRepository
from app.authorization.repositories.policy_repository import PolicyRepository
from app.authorization.repositories.role_repository import RoleRepository
from app.authorization.services.authorization_service import AuthorizationService
from app.core.settings import AppSettings
from app.dependencies.providers import provide_database_session, provide_redis_client, provide_settings


def build_authorization_service(
    session: AsyncSession,
    redis_client: Redis,
    settings: AppSettings,
) -> AuthorizationService:
    role_repository = RoleRepository(session)
    permission_repository = PermissionRepository(session)
    policy_repository = PolicyRepository(session)
    cache_repository = AuthorizationCacheRepository(redis_client)
    return AuthorizationService(
        role_repository=role_repository,
        permission_repository=permission_repository,
        policy_repository=policy_repository,
        cache_repository=cache_repository,
        settings=settings,
        logger=__import__("logging").getLogger("sentinel.authorization"),
        audit_logger=__import__("logging").getLogger("sentinel.audit"),
    )


def provide_authorization_service(
    session: AsyncSession = Depends(provide_database_session),
    redis_client: Redis = Depends(provide_redis_client),
    settings: AppSettings = Depends(provide_settings),
) -> AuthorizationService:
    return build_authorization_service(session, redis_client, settings)


async def provide_authorization_context(
    request: Request,
    auth_context: AuthContext = Depends(provide_auth_context),
    authorization_service: AuthorizationService = Depends(provide_authorization_service),
) -> AuthorizationContext:
    cached_context = getattr(request.state, "authorization_context", None)
    if cached_context is not None:
        return cached_context
    context = await authorization_service.build_context(auth_context)
    request.state.authorization_context = context
    return context


async def provide_optional_authorization_context(
    request: Request,
    auth_context: AuthContext | None = Depends(provide_optional_auth_context),
    authorization_service: AuthorizationService = Depends(provide_authorization_service),
) -> AuthorizationContext | None:
    if auth_context is None:
        return None
    return await provide_authorization_context(request, auth_context, authorization_service)

