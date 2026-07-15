from __future__ import annotations

from contextlib import asynccontextmanager
from dataclasses import dataclass
from datetime import UTC, datetime
from typing import Any, AsyncIterator
from uuid import UUID

from sqlalchemy import delete, func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.prompt.models import (
    Prompt,
    PromptAnalytics,
    PromptApproval,
    PromptAudit,
    PromptCategory,
    PromptExecution,
    PromptPolicy,
    PromptTemplate,
    PromptTemplateSeed,
    PromptVariable,
    PromptVersion,
)


@dataclass(slots=True)
class PromptRepository:
    """Async prompt persistence helpers."""

    session: AsyncSession

    @asynccontextmanager
    async def transaction(self) -> AsyncIterator[AsyncSession]:
        async with self.session.begin():
            yield self.session

    async def list_categories(self) -> list[PromptCategory]:
        result = await self.session.execute(select(PromptCategory).where(PromptCategory.deleted_at.is_(None)).order_by(PromptCategory.name))
        return list(result.scalars().all())

    async def get_category_by_code(self, code: str) -> PromptCategory | None:
        result = await self.session.execute(select(PromptCategory).where(PromptCategory.code == code, PromptCategory.deleted_at.is_(None)))
        return result.scalar_one_or_none()

    async def upsert_category(self, *, code: str, name: str, description: str | None, status: str = "active", metadata: dict[str, object] | None = None) -> PromptCategory:
        category = await self.get_category_by_code(code)
        if category is None:
            category = PromptCategory(code=code, name=name, description=description, status=status, category_metadata=metadata or {})
            self.session.add(category)
        else:
            category.name = name
            category.description = description
            category.status = status
            category.category_metadata = metadata or {}
        await self.session.flush()
        return category

    async def list_prompts(self, search: str | None = None, status: str | None = None, category_code: str | None = None) -> list[Prompt]:
        statement = select(Prompt).options(
            selectinload(Prompt.category),
            selectinload(Prompt.templates),
            selectinload(Prompt.versions),
            selectinload(Prompt.variables),
            selectinload(Prompt.policies),
            selectinload(Prompt.approvals),
        ).where(Prompt.deleted_at.is_(None))
        if search:
            statement = statement.where(or_(Prompt.name.ilike(f"%{search}%"), Prompt.code.ilike(f"%{search}%"), Prompt.description.ilike(f"%{search}%")))
        if status:
            statement = statement.where(Prompt.status == status)
        if category_code:
            statement = statement.join(PromptCategory, Prompt.category_id == PromptCategory.id).where(PromptCategory.code == category_code)
        result = await self.session.execute(statement.order_by(Prompt.updated_at.desc()))
        return list(result.scalars().unique().all())

    async def get_prompt(self, prompt_id: UUID) -> Prompt | None:
        result = await self.session.execute(
            select(Prompt).options(
                selectinload(Prompt.category),
                selectinload(Prompt.templates),
                selectinload(Prompt.versions),
                selectinload(Prompt.variables),
                selectinload(Prompt.policies),
                selectinload(Prompt.executions),
                selectinload(Prompt.audits),
                selectinload(Prompt.approvals),
                selectinload(Prompt.analytics),
            ).where(Prompt.id == prompt_id)
        )
        prompt = result.scalar_one_or_none()
        if prompt is None or prompt.deleted_at is not None:
            return None
        return prompt

    async def get_prompt_by_code(self, code: str) -> Prompt | None:
        result = await self.session.execute(select(Prompt).where(Prompt.code == code, Prompt.deleted_at.is_(None)))
        return result.scalar_one_or_none()

    async def create_prompt(self, prompt: Prompt) -> Prompt:
        self.session.add(prompt)
        await self.session.flush()
        return prompt

    async def update_prompt(self, prompt: Prompt, values: dict[str, Any]) -> Prompt:
        for key, value in values.items():
            if hasattr(prompt, key):
                setattr(prompt, key, value)
        await self.session.flush()
        return prompt

    async def delete_prompt(self, prompt: Prompt) -> Prompt:
        prompt.mark_deleted()
        prompt.status = "archived"
        await self.session.flush()
        return prompt

    async def create_template(self, template: PromptTemplate) -> PromptTemplate:
        self.session.add(template)
        await self.session.flush()
        return template

    async def create_version(self, version: PromptVersion) -> PromptVersion:
        self.session.add(version)
        await self.session.flush()
        return version

    async def list_versions(self, prompt_id: UUID) -> list[PromptVersion]:
        result = await self.session.execute(
            select(PromptVersion).where(PromptVersion.prompt_id == prompt_id, PromptVersion.deleted_at.is_(None)).order_by(PromptVersion.version_number.desc())
        )
        return list(result.scalars().all())

    async def get_version(self, version_id: UUID) -> PromptVersion | None:
        result = await self.session.execute(select(PromptVersion).where(PromptVersion.id == version_id))
        version = result.scalar_one_or_none()
        if version is None or version.deleted_at is not None:
            return None
        return version

    async def add_variable(self, variable: PromptVariable) -> PromptVariable:
        self.session.add(variable)
        await self.session.flush()
        return variable

    async def add_policy(self, policy: PromptPolicy) -> PromptPolicy:
        self.session.add(policy)
        await self.session.flush()
        return policy

    async def add_execution(self, execution: PromptExecution) -> PromptExecution:
        self.session.add(execution)
        await self.session.flush()
        return execution

    async def add_audit(self, audit: PromptAudit) -> PromptAudit:
        self.session.add(audit)
        await self.session.flush()
        return audit

    async def add_approval(self, approval: PromptApproval) -> PromptApproval:
        self.session.add(approval)
        await self.session.flush()
        return approval

    async def add_analytics(self, analytics: PromptAnalytics) -> PromptAnalytics:
        self.session.add(analytics)
        await self.session.flush()
        return analytics

    async def list_analytics(self, prompt_id: UUID | None = None) -> list[PromptAnalytics]:
        statement = select(PromptAnalytics).order_by(PromptAnalytics.metric_date.desc())
        if prompt_id is not None:
            statement = statement.where(PromptAnalytics.prompt_id == prompt_id)
        result = await self.session.execute(statement)
        return list(result.scalars().all())

    async def create_seed_template(self, seed: PromptTemplateSeed) -> PromptTemplateSeed:
        self.session.add(seed)
        await self.session.flush()
        return seed

    async def list_seed_templates(self) -> list[PromptTemplateSeed]:
        result = await self.session.execute(select(PromptTemplateSeed))
        return list(result.scalars().all())
