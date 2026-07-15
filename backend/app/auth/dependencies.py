from __future__ import annotations

from fastapi import Depends, Request
from redis.asyncio import Redis
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.middleware import extract_bearer_token
from app.auth.models import AuthContext
from app.auth.repositories.auth_repository import AuthRepository
from app.auth.security.password_hasher import PasswordHasher
from app.auth.services.auth_service import AuthService
from app.auth.tokens.generator import TokenGenerator
from app.auth.tokens.repository import TokenRepository
from app.auth.tokens.service import JwtService
from app.auth.tokens.validator import TokenValidator
from app.auth.emails.smtp import SmtpEmailClient
from app.core.settings import AppSettings
from app.exceptions.base import AuthenticationApplicationException
from app.dependencies.providers import (
    get_audit_logger,
    get_logger,
    provide_database_session,
    provide_redis_client,
    provide_settings,
)


def provide_jwt_service(settings: AppSettings = Depends(provide_settings)) -> JwtService:
    return JwtService(settings)


def provide_password_hasher() -> PasswordHasher:
    return PasswordHasher()


def provide_token_repository(
    redis_client: Redis = Depends(provide_redis_client),
    settings: AppSettings = Depends(provide_settings),
) -> TokenRepository:
    return TokenRepository(redis_client=redis_client, jwt_service=JwtService(settings))


def provide_auth_repository(session: AsyncSession = Depends(provide_database_session)) -> AuthRepository:
    return AuthRepository(session)


def provide_token_generator(
    settings: AppSettings = Depends(provide_settings),
    jwt_service: JwtService = Depends(provide_jwt_service),
) -> TokenGenerator:
    return TokenGenerator(settings=settings, jwt_service=jwt_service)


def provide_token_validator(jwt_service: JwtService = Depends(provide_jwt_service)) -> TokenValidator:
    return TokenValidator(jwt_service=jwt_service)


def provide_email_client(settings: AppSettings = Depends(provide_settings)) -> SmtpEmailClient:
    return SmtpEmailClient(settings)


def provide_auth_service(
    repository: AuthRepository = Depends(provide_auth_repository),
    settings: AppSettings = Depends(provide_settings),
    jwt_service: JwtService = Depends(provide_jwt_service),
    token_generator: TokenGenerator = Depends(provide_token_generator),
    token_validator: TokenValidator = Depends(provide_token_validator),
    token_repository: TokenRepository = Depends(provide_token_repository),
    password_hasher: PasswordHasher = Depends(provide_password_hasher),
    email_client: SmtpEmailClient = Depends(provide_email_client),
) -> AuthService:
    return AuthService(
        repository=repository,
        settings=settings,
        jwt_service=jwt_service,
        token_generator=token_generator,
        token_validator=token_validator,
        token_repository=token_repository,
        password_hasher=password_hasher,
        email_client=email_client,
        logger=get_logger(),
        audit_logger=get_audit_logger(),
    )


def provide_auth_context(
    request: Request,
    token_validator: TokenValidator = Depends(provide_token_validator),
) -> AuthContext:
    cached_context = getattr(request.state, "auth_context", None)
    if cached_context is not None:
        return cached_context
    token = extract_bearer_token(request)
    if token is None:
        raise AuthenticationApplicationException("Authentication required")
    return token_validator.validate_access_token(token)


def provide_optional_auth_context(
    request: Request,
    token_validator: TokenValidator = Depends(provide_token_validator),
) -> AuthContext | None:
    cached_context = getattr(request.state, "auth_context", None)
    if cached_context is not None:
        return cached_context
    token = extract_bearer_token(request)
    if token is None:
        return None
    return token_validator.validate_access_token(token)
