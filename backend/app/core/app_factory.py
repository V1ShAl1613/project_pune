from __future__ import annotations

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from starlette.middleware.trustedhost import TrustedHostMiddleware

from app.authorization.controllers.router import router as authorization_router
from app.authorization.middlewares.authorization import AuthorizationMiddleware
from app.ai.controllers.router import router as ai_router
from app.api.v1.router import router as v1_router
from app.auth.controllers.router import router as auth_router
from app.auth.middleware import AuthenticationMiddleware
from app.agents.controllers.router import router as agents_router
from app.core.settings import AppSettings, get_settings
from app.database.redis import get_redis_manager
from app.dependencies.providers import provide_redis_client, provide_settings
from app.identity.controllers.router import router as identity_router
from app.exceptions.handlers import register_exception_handlers
from app.health.router import router as health_router
from app.logging.config import configure_logging
from app.middlewares.correlation_id import CorrelationIdMiddleware
from app.middlewares.exception import ExceptionLoggingMiddleware
from app.middlewares.request_logging import RequestLoggingMiddleware
from app.middlewares.security_headers import SecurityHeadersMiddleware
from app.middlewares.timing import RequestTimingMiddleware
from app.metrics.router import router as metrics_router
from app.reasoning.controllers.router import router as reasoning_router
from app.banking.controllers.router import router as banking_router
from app.grc.controllers.router import router as grc_router
from app.threat.controllers.router import router as threat_router
from app.knowledge.controllers.router import router as knowledge_router
from app.prompt.controllers.router import router as prompt_router
from app.routers.root import router as root_router


def create_app(settings: AppSettings | None = None) -> FastAPI:
    resolved_settings = settings or get_settings()
    configure_logging(resolved_settings)

    app = FastAPI(
        title=resolved_settings.app_name,
        version="1.0.0",
        debug=resolved_settings.debug,
        docs_url="/docs" if resolved_settings.enable_docs else None,
        redoc_url="/redoc" if resolved_settings.enable_redoc else None,
        openapi_url="/openapi.json",
    )

    if resolved_settings.cors_origins:
        app.add_middleware(
            CORSMiddleware,
            allow_origins=resolved_settings.cors_origins,
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )

    if resolved_settings.enable_compression:
        app.add_middleware(GZipMiddleware, minimum_size=1000)

    if resolved_settings.enable_trusted_hosts and resolved_settings.trusted_hosts:
        app.add_middleware(TrustedHostMiddleware, allowed_hosts=resolved_settings.trusted_hosts)

    app.add_middleware(CorrelationIdMiddleware, header_name=resolved_settings.correlation_header)
    app.add_middleware(AuthenticationMiddleware, settings=resolved_settings)
    app.add_middleware(AuthorizationMiddleware, settings=resolved_settings)
    app.add_middleware(SecurityHeadersMiddleware, settings=resolved_settings)
    app.add_middleware(RequestTimingMiddleware)
    app.add_middleware(RequestLoggingMiddleware)
    app.add_middleware(ExceptionLoggingMiddleware)

    register_exception_handlers(app)
    app.state.settings = resolved_settings
    app.state.session_factory = __import__("app.database.session", fromlist=["get_session_factory"]).get_session_factory(resolved_settings)
    app.state.redis_manager = get_redis_manager(resolved_settings)
    app.state.redis_client = app.state.redis_manager.get_client()
    app.state.redis_dependency = provide_redis_client
    app.state.settings_dependency = provide_settings

    v1_prefix = resolved_settings.api_v1_prefix
    app.include_router(root_router)
    app.include_router(auth_router, prefix=v1_prefix)
    app.include_router(grc_router, prefix=v1_prefix)
    app.include_router(authorization_router, prefix=v1_prefix)
    app.include_router(ai_router, prefix=v1_prefix)
    app.include_router(agents_router, prefix=v1_prefix)
    app.include_router(reasoning_router, prefix=v1_prefix)
    app.include_router(banking_router, prefix=v1_prefix)
    app.include_router(threat_router, prefix=v1_prefix)
    app.include_router(prompt_router, prefix=v1_prefix)
    app.include_router(knowledge_router, prefix=v1_prefix)
    app.include_router(identity_router, prefix=f"{v1_prefix}/identity")
    app.include_router(health_router)
    app.include_router(metrics_router)
    app.include_router(v1_router)
    return app
