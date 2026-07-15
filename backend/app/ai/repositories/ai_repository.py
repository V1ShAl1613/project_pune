from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC, datetime
from typing import Any
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.ai.models import AIModel, AIProvider, AISettings, Conversation, ConversationMessage, InferenceLog, ModelConfiguration, ProviderHealth


@dataclass(slots=True)
class AIRepository:
    session: AsyncSession

    async def list_providers(self) -> list[AIProvider]:
        result = await self.session.execute(select(AIProvider).where(AIProvider.deleted_at.is_(None)).order_by(AIProvider.priority, AIProvider.name))
        return list(result.scalars().all())

    async def get_provider(self, provider_id: UUID) -> AIProvider | None:
        provider = await self.session.get(AIProvider, provider_id)
        if provider is None or provider.deleted_at is not None:
            return None
        return provider

    async def get_provider_by_name(self, name: str) -> AIProvider | None:
        result = await self.session.execute(select(AIProvider).where(AIProvider.name == name, AIProvider.deleted_at.is_(None)))
        return result.scalar_one_or_none()

    async def upsert_provider(self, *, name: str, provider_type: str, base_url: str | None, status: str = "active", priority: int = 100, provider_metadata: dict[str, object] | None = None) -> AIProvider:
        provider = await self.get_provider_by_name(name)
        payload = provider_metadata or {}
        if provider is None:
            provider = AIProvider(name=name, provider_type=provider_type, base_url=base_url, status=status, priority=priority, provider_metadata=payload)
            self.session.add(provider)
        else:
            provider.provider_type = provider_type
            provider.base_url = base_url
            provider.status = status
            provider.priority = priority
            provider.provider_metadata = payload
        await self.session.flush()
        return provider

    async def list_models(self) -> list[AIModel]:
        result = await self.session.execute(
            select(AIModel)
            .options(selectinload(AIModel.provider))
            .where(AIModel.deleted_at.is_(None))
            .order_by(AIModel.is_default.desc(), AIModel.priority, AIModel.name)
        )
        return list(result.scalars().all())

    async def get_model(self, model_id: UUID) -> AIModel | None:
        result = await self.session.execute(select(AIModel).options(selectinload(AIModel.provider)).where(AIModel.id == model_id))
        model = result.scalar_one_or_none()
        if model is None or model.deleted_at is not None:
            return None
        return model

    async def get_model_by_name(self, provider_id: UUID, name: str) -> AIModel | None:
        result = await self.session.execute(
            select(AIModel).options(selectinload(AIModel.provider)).where(AIModel.provider_id == provider_id, AIModel.name == name, AIModel.deleted_at.is_(None))
        )
        return result.scalar_one_or_none()

    async def upsert_model(
        self,
        *,
        provider_id: UUID,
        name: str,
        display_name: str,
        model_type: str = "local",
        status: str = "available",
        model_version: str | None = None,
        context_length: int = 8192,
        supports_streaming: bool = True,
        supports_json: bool = True,
        supports_structured: bool = True,
        default_temperature: float = 0.2,
        default_top_p: float = 0.95,
        priority: int = 100,
        is_default: bool = False,
        tags: dict[str, object] | None = None,
        configuration: dict[str, object] | None = None,
        model_metadata: dict[str, object] | None = None,
    ) -> AIModel:
        model = await self.get_model_by_name(provider_id, name)
        if model is None:
            model = AIModel(
                provider_id=provider_id,
                name=name,
                display_name=display_name,
                model_type=model_type,
                status=status,
                model_version=model_version,
                context_length=context_length,
                supports_streaming=supports_streaming,
                supports_json=supports_json,
                supports_structured=supports_structured,
                default_temperature=default_temperature,
                default_top_p=default_top_p,
                priority=priority,
                is_default=is_default,
                tags=tags or {},
                configuration=configuration or {},
                model_metadata=model_metadata or {},
            )
            self.session.add(model)
        else:
            model.display_name = display_name
            model.model_type = model_type
            model.status = status
            model.model_version = model_version
            model.context_length = context_length
            model.supports_streaming = supports_streaming
            model.supports_json = supports_json
            model.supports_structured = supports_structured
            model.default_temperature = default_temperature
            model.default_top_p = default_top_p
            model.priority = priority
            model.is_default = is_default
            model.tags = tags or {}
            model.configuration = configuration or {}
            model.model_metadata = model_metadata or {}
        await self.session.flush()
        return model

    async def delete_model(self, model: AIModel) -> None:
        model.mark_deleted()
        model.status = "deleted"
        await self.session.flush()

    async def list_conversations(self) -> list[Conversation]:
        result = await self.session.execute(
            select(Conversation).options(selectinload(Conversation.messages)).where(Conversation.deleted_at.is_(None)).order_by(Conversation.updated_at.desc())
        )
        return list(result.scalars().unique().all())

    async def get_conversation(self, conversation_id: UUID) -> Conversation | None:
        result = await self.session.execute(
            select(Conversation).options(selectinload(Conversation.messages)).where(Conversation.id == conversation_id)
        )
        conversation = result.scalar_one_or_none()
        if conversation is None or conversation.deleted_at is not None:
            return None
        return conversation

    async def create_conversation(self, conversation: Conversation) -> Conversation:
        self.session.add(conversation)
        await self.session.flush()
        return conversation

    async def delete_conversation(self, conversation: Conversation) -> Conversation:
        conversation.mark_deleted()
        conversation.status = "archived"
        await self.session.flush()
        return conversation

    async def add_message(self, message: ConversationMessage) -> ConversationMessage:
        self.session.add(message)
        await self.session.flush()
        return message

    async def list_model_configurations(self, model_id: UUID) -> list[ModelConfiguration]:
        result = await self.session.execute(select(ModelConfiguration).where(ModelConfiguration.model_id == model_id))
        return list(result.scalars().all())

    async def log_inference(self, log: InferenceLog) -> InferenceLog:
        self.session.add(log)
        await self.session.flush()
        return log

    async def record_health(self, health: ProviderHealth) -> ProviderHealth:
        self.session.add(health)
        await self.session.flush()
        return health

    async def get_ai_setting(self, name: str) -> AISettings | None:
        result = await self.session.execute(select(AISettings).where(AISettings.name == name, AISettings.deleted_at.is_(None)))
        return result.scalar_one_or_none()
