"""FastAPI dependency providers for the agent platform."""

from __future__ import annotations

from functools import lru_cache

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.agents.repositories.agent_repository import AgentRepository
from app.agents.services.agent_service import AgentService
from app.dependencies.providers import provide_database_session


@lru_cache(maxsize=1)
def get_agent_service_class() -> type[AgentService]:
    return AgentService


def provide_agent_repository(session: AsyncSession = Depends(provide_database_session)) -> AgentRepository:
    return AgentRepository(session)


def provide_agent_service(session: AsyncSession = Depends(provide_database_session)) -> AgentService:
    return AgentService(repository=AgentRepository(session))
