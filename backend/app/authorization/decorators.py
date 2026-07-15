from __future__ import annotations

from functools import wraps
from typing import Awaitable, Callable, TypeVar

from fastapi import Request

from app.authorization.dependencies import build_authorization_service
from app.exceptions.base import AuthenticationApplicationException, AuthorizationApplicationException

EndpointCallable = TypeVar("EndpointCallable", bound=Callable[..., Awaitable[object]])


def _get_request(args: tuple[object, ...], kwargs: dict[str, object]) -> Request:
    request = kwargs.get("request")
    if isinstance(request, Request):
        return request
    for value in args:
        if isinstance(value, Request):
            return value
    raise RuntimeError("Authorization decorators require a Request parameter")


def _build_guarded_service(request: Request):
    session_factory = getattr(request.app.state, "session_factory", None)
    redis_client = getattr(request.app.state, "redis_client", None)
    settings = getattr(request.app.state, "settings", None)
    if session_factory is None or redis_client is None or settings is None:
        raise RuntimeError("Authorization service state is not configured")
    return session_factory, redis_client, settings


def RequirePermission(permission_code: str):
    def decorator(endpoint: EndpointCallable) -> EndpointCallable:
        @wraps(endpoint)
        async def wrapper(*args, **kwargs):
            request = _get_request(args, kwargs)
            auth_context = getattr(request.state, "auth_context", None)
            if auth_context is None:
                raise AuthenticationApplicationException("Authentication required", status_code=401, error_code="authentication_error")
            session_factory, redis_client, settings = _build_guarded_service(request)
            async with session_factory() as session:
                service = build_authorization_service(session, redis_client, settings)
                decision = await service.authorize(auth_context, resource=permission_code.split(".", 1)[0], action=permission_code.split(".", 1)[1] if "." in permission_code else permission_code, permission_code=permission_code)
                if not decision.allowed:
                    raise AuthorizationApplicationException(decision.reason, status_code=403, error_code="authorization_error")
                return await endpoint(*args, **kwargs)

        return wrapper  # type: ignore[return-value]

    return decorator


def RequireAnyPermission(*permission_codes: str):
    def decorator(endpoint: EndpointCallable) -> EndpointCallable:
        @wraps(endpoint)
        async def wrapper(*args, **kwargs):
            request = _get_request(args, kwargs)
            auth_context = getattr(request.state, "auth_context", None)
            if auth_context is None:
                raise AuthenticationApplicationException("Authentication required", status_code=401, error_code="authentication_error")
            session_factory, redis_client, settings = _build_guarded_service(request)
            async with session_factory() as session:
                service = build_authorization_service(session, redis_client, settings)
                decision = await service.authorize(
                    auth_context,
                    resource="authorization",
                    action="access",
                    any_permission_codes=list(permission_codes),
                )
                if not decision.allowed:
                    raise AuthorizationApplicationException(decision.reason, status_code=403, error_code="authorization_error")
                return await endpoint(*args, **kwargs)

        return wrapper  # type: ignore[return-value]

    return decorator


def RequireRole(role_code: str):
    def decorator(endpoint: EndpointCallable) -> EndpointCallable:
        @wraps(endpoint)
        async def wrapper(*args, **kwargs):
            request = _get_request(args, kwargs)
            auth_context = getattr(request.state, "auth_context", None)
            if auth_context is None:
                raise AuthenticationApplicationException("Authentication required", status_code=401, error_code="authentication_error")
            session_factory, redis_client, settings = _build_guarded_service(request)
            async with session_factory() as session:
                service = build_authorization_service(session, redis_client, settings)
                decision = await service.authorize(auth_context, resource="authorization", action="access", role_code=role_code)
                if not decision.allowed:
                    raise AuthorizationApplicationException(decision.reason, status_code=403, error_code="authorization_error")
                return await endpoint(*args, **kwargs)

        return wrapper  # type: ignore[return-value]

    return decorator


def RequireAnyRole(*role_codes: str):
    def decorator(endpoint: EndpointCallable) -> EndpointCallable:
        @wraps(endpoint)
        async def wrapper(*args, **kwargs):
            request = _get_request(args, kwargs)
            auth_context = getattr(request.state, "auth_context", None)
            if auth_context is None:
                raise AuthenticationApplicationException("Authentication required", status_code=401, error_code="authentication_error")
            session_factory, redis_client, settings = _build_guarded_service(request)
            async with session_factory() as session:
                service = build_authorization_service(session, redis_client, settings)
                decision = await service.authorize(auth_context, resource="authorization", action="access", any_role_codes=list(role_codes))
                if not decision.allowed:
                    raise AuthorizationApplicationException(decision.reason, status_code=403, error_code="authorization_error")
                return await endpoint(*args, **kwargs)

        return wrapper  # type: ignore[return-value]

    return decorator


def RequireOwnership(owner_id_field: str):
    def decorator(endpoint: EndpointCallable) -> EndpointCallable:
        @wraps(endpoint)
        async def wrapper(*args, **kwargs):
            request = _get_request(args, kwargs)
            auth_context = getattr(request.state, "auth_context", None)
            if auth_context is None:
                raise AuthenticationApplicationException("Authentication required", status_code=401, error_code="authentication_error")
            owner_id = kwargs.get(owner_id_field)
            session_factory, redis_client, settings = _build_guarded_service(request)
            async with session_factory() as session:
                service = build_authorization_service(session, redis_client, settings)
                decision = await service.authorize(auth_context, resource="authorization", action="access", owner_id=owner_id)
                if not decision.allowed:
                    raise AuthorizationApplicationException(decision.reason, status_code=403, error_code="authorization_error")
                return await endpoint(*args, **kwargs)

        return wrapper  # type: ignore[return-value]

    return decorator

