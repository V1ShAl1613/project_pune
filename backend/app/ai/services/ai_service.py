from __future__ import annotations

import json
import logging
from dataclasses import dataclass
from datetime import UTC, datetime, timedelta
from uuid import uuid4

from redis.asyncio import Redis

from app.ai.clients.ollama_client import OllamaClient
from app.ai.models import AIModel, AIProvider, Conversation, ConversationMessage, InferenceLog, ProviderHealth
from app.ai.repositories.ai_repository import AIRepository
from app.ai.schemas import (
    AIChatRequest,
    AICompletionRequest,
    AIHealthResponse,
    AIModelPullRequest,
    AIModelResponse,
    AIProviderResponse,
    AIResponse,
    ConversationCreateRequest,
    ConversationResponse,
)
from app.core.settings import AppSettings
from app.exceptions.base import BaseApplicationException


@dataclass(slots=True)
class AIService:
    repository: AIRepository
    settings: AppSettings
    ollama_client: OllamaClient
    redis_client: Redis | None
    logger: logging.Logger

    async def list_models(self) -> list[AIModelResponse]:
        await self._ensure_default_catalog()
        cached = await self._cache_get("ai:models:list")
        if cached:
            return [AIModelResponse.model_validate(item) for item in cached]
        models = await self.repository.list_models()
        payload = [AIModelResponse.model_validate(model, from_attributes=True).model_dump(mode="json") for model in models]
        await self._cache_set("ai:models:list", payload, ttl=60)
        return [AIModelResponse.model_validate(item) for item in payload]

    async def get_model(self, model_id) -> AIModelResponse:
        model = await self.repository.get_model(model_id)
        if model is None:
            raise BaseApplicationException("Model not found", status_code=404, error_code="ai_model_not_found")
        return AIModelResponse.model_validate(model, from_attributes=True)

    async def list_providers(self) -> list[AIProviderResponse]:
        await self._ensure_default_catalog()
        cached = await self._cache_get("ai:providers:list")
        if cached:
            return [AIProviderResponse.model_validate(item) for item in cached]
        providers = await self.repository.list_providers()
        payload = [AIProviderResponse.model_validate(provider, from_attributes=True).model_dump(mode="json") for provider in providers]
        await self._cache_set("ai:providers:list", payload, ttl=60)
        return [AIProviderResponse.model_validate(item) for item in payload]

    async def pull_model(self, request: AIModelPullRequest) -> AIModelResponse:
        provider = await self._resolve_provider(request.provider_name)
        result = await self.ollama_client.pull_model(request.name)
        model = await self.repository.upsert_model(
            provider_id=provider.id,
            name=request.name,
            display_name=request.name,
            model_type=provider.provider_type,
            status="available",
            is_default=request.name == self.settings.ai_default_model,
            model_metadata={"pull_result": result},
        )
        await self._invalidate_catalog_cache()
        await self._record_health(provider, model, status="healthy", metadata={"pulled": True})
        return AIModelResponse.model_validate(model, from_attributes=True)

    async def delete_model(self, model_id) -> None:
        model = await self.repository.get_model(model_id)
        if model is None:
            raise BaseApplicationException("Model not found", status_code=404, error_code="ai_model_not_found")
        await self.repository.delete_model(model)
        await self._invalidate_catalog_cache()

    async def health(self) -> AIHealthResponse:
        await self._ensure_default_catalog()
        cached = await self._cache_get("ai:health:snapshot")
        if cached:
            return AIHealthResponse.model_validate(cached)

        providers = await self.list_providers()
        models = await self.list_models()
        provider_health = await self.ollama_client.health()
        payload = {
            "status": "healthy" if providers else "degraded",
            "providers": [provider.model_dump(mode="json") for provider in providers],
            "models": [model.model_dump(mode="json") for model in models],
            "metrics": {
                "ollama": provider_health,
                "enabled": self.settings.ai_gateway_enabled,
                "streaming": self.settings.ai_enable_streaming,
            },
        }
        await self._cache_set("ai:health:snapshot", payload, ttl=30)
        return AIHealthResponse.model_validate(payload)

    async def chat(self, request: AIChatRequest) -> AIResponse:
        model = await self._select_model(request.model)
        messages = [message.model_dump() for message in request.messages]
        options = self._build_options(request.temperature, request.top_p, request.max_tokens)
        result = await self.ollama_client.chat(model=model.name, messages=messages, options=options)
        content = self._extract_message_content(result)
        response = AIResponse(
            id=str(uuid4()),
            provider=model.provider.provider_type,
            model=model.name,
            content=content,
            created_at=datetime.now(UTC),
            metadata={"conversation_id": str(request.conversation_id) if request.conversation_id else None, "raw": result},
        )
        await self._log_inference(model, request.model_dump(mode="json"), response, request.conversation_id)
        if request.conversation_id is not None:
            await self._append_conversation_exchange(request.conversation_id, request.messages, content)
        return response

    async def completion(self, request: AICompletionRequest) -> AIResponse:
        model = await self._select_model(request.model)
        options = self._build_options(request.temperature, request.top_p, request.max_tokens)
        result = await self.ollama_client.generate(model=model.name, prompt=request.prompt, options=options)
        content = result.get("response", "") if isinstance(result, dict) else ""
        response = AIResponse(
            id=str(uuid4()),
            provider=model.provider.provider_type,
            model=model.name,
            content=content,
            created_at=datetime.now(UTC),
            metadata={"raw": result},
        )
        await self._log_inference(model, request.model_dump(mode="json"), response, None)
        return response

    async def stream_chat(self, request: AIChatRequest):
        model = await self._select_model(request.model)
        messages = [message.model_dump() for message in request.messages]
        options = self._build_options(request.temperature, request.top_p, request.max_tokens)
        async for chunk in self.ollama_client.stream_chat(model=model.name, messages=messages, options=options):
            yield f"data: {json.dumps({'id': str(uuid4()), 'provider': model.provider.provider_type, 'model': model.name, 'chunk': chunk, 'done': False})}\n\n"
        yield f"data: {json.dumps({'id': str(uuid4()), 'provider': model.provider.provider_type, 'model': model.name, 'chunk': '', 'done': True})}\n\n"

    async def create_conversation(self, request: ConversationCreateRequest) -> ConversationResponse:
        model = await self._select_model(request.model)
        conversation = Conversation(
            tenant_id=request.tenant_id,
            user_id=request.user_id,
            title=request.title,
            status="active",
            model_name=model.name,
            model_provider=model.provider.provider_type,
            conversation_metadata=request.metadata,
            context_window=model.context_length,
            last_message_at=None,
            expires_at=datetime.now(UTC) + timedelta(days=30),
        )
        await self.repository.create_conversation(conversation)
        return await self.get_conversation(conversation.id)

    async def get_conversation(self, conversation_id) -> ConversationResponse:
        conversation = await self.repository.get_conversation(conversation_id)
        if conversation is None:
            raise BaseApplicationException("Conversation not found", status_code=404, error_code="ai_conversation_not_found")
        return ConversationResponse(
            id=conversation.id,
            tenant_id=conversation.tenant_id,
            user_id=conversation.user_id,
            title=conversation.title,
            status=conversation.status,
            model_name=conversation.model_name,
            model_provider=conversation.model_provider,
            conversation_metadata=conversation.conversation_metadata,
            context_window=conversation.context_window,
            last_message_at=conversation.last_message_at,
            expires_at=conversation.expires_at,
            created_at=conversation.created_at,
            updated_at=conversation.updated_at,
            messages=[
                {
                    "id": message.id,
                    "conversation_id": message.conversation_id,
                    "role": message.role,
                    "content": message.content,
                    "sequence": message.sequence,
                    "message_metadata": message.message_metadata,
                    "token_count": message.token_count,
                    "created_at": message.created_at,
                }
                for message in conversation.messages
            ],
        )

    async def delete_conversation(self, conversation_id) -> None:
        conversation = await self.repository.get_conversation(conversation_id)
        if conversation is None:
            raise BaseApplicationException("Conversation not found", status_code=404, error_code="ai_conversation_not_found")
        await self.repository.delete_conversation(conversation)

    async def list_conversations(self) -> list[ConversationResponse]:
        conversations = await self.repository.list_conversations()
        return [await self.get_conversation(conversation.id) for conversation in conversations]

    async def _ensure_default_catalog(self) -> None:
        provider = await self.repository.get_provider_by_name("ollama")
        if provider is None:
            provider = await self.repository.upsert_provider(
                name="ollama",
                provider_type="ollama",
                base_url=self.settings.ai_ollama_base_url,
                priority=1,
                provider_metadata={"runtime": "local-ollama", "gateway": "enterprise-ai"},
            )
        existing_models = await self.repository.list_models()
        if not existing_models:
            await self.repository.upsert_model(
                provider_id=provider.id,
                name=self.settings.ai_default_model,
                display_name=self.settings.ai_default_model,
                model_type="ollama",
                status="available",
                is_default=True,
                model_metadata={"seeded": True},
            )
        await self._invalidate_catalog_cache()

    async def _resolve_provider(self, provider_name: str | None) -> AIProvider:
        resolved_name = provider_name or self.settings.ai_default_provider
        provider = await self.repository.get_provider_by_name(resolved_name)
        if provider is None:
            provider = await self.repository.upsert_provider(
                name=resolved_name,
                provider_type=resolved_name,
                base_url=self.settings.ai_ollama_base_url if resolved_name == "ollama" else None,
                provider_metadata={"auto_created": True},
            )
        return provider

    async def _select_model(self, model_name: str | None) -> AIModel:
        models = await self.repository.list_models()
        if not models:
            await self._ensure_default_catalog()
            models = await self.repository.list_models()
        if model_name:
            for model in models:
                if model.name == model_name:
                    return model
        for model in models:
            if model.is_default:
                return model
        if models:
            return models[0]
        raise BaseApplicationException("No AI models are available", status_code=503, error_code="ai_model_unavailable")

    def _build_options(self, temperature: float | None, top_p: float | None, max_tokens: int | None) -> dict[str, object]:
        options: dict[str, object] = {}
        if temperature is not None:
            options["temperature"] = temperature
        if top_p is not None:
            options["top_p"] = top_p
        if max_tokens is not None:
            options["num_predict"] = max_tokens
        return options

    async def _log_inference(
        self,
        model: AIModel,
        request_payload: dict[str, object],
        response: AIResponse,
        conversation_id,
    ) -> None:
        await self.repository.log_inference(
            InferenceLog(
                model_id=model.id,
                conversation_id=conversation_id,
                request_id=response.id,
                prompt=json.dumps(request_payload),
                response=response.content,
                request_metadata=request_payload,
                response_metadata=response.metadata,
                status="success",
                latency_ms=0,
                token_count=0,
                provider_name=model.provider.provider_type,
            )
        )

    async def _append_conversation_exchange(self, conversation_id, messages, assistant_content: str) -> None:
        conversation = await self.repository.get_conversation(conversation_id)
        if conversation is None:
            return
        sequence = len(conversation.messages)
        for message in messages:
            sequence += 1
            await self.repository.add_message(
                ConversationMessage(
                    conversation_id=conversation.id,
                    role=message.role,
                    content=message.content,
                    sequence=sequence,
                    message_metadata={},
                    token_count=len(message.content.split()),
                )
            )
        await self.repository.add_message(
            ConversationMessage(
                conversation_id=conversation.id,
                role="assistant",
                content=assistant_content,
                sequence=sequence + 1,
                message_metadata={},
                token_count=len(assistant_content.split()),
            )
        )
        conversation.last_message_at = datetime.now(UTC)
        await self.repository.session.flush()

    def _extract_message_content(self, payload: dict[str, object]) -> str:
        message = payload.get("message") if isinstance(payload, dict) else None
        if isinstance(message, dict):
            content = message.get("content")
            if isinstance(content, str):
                return content
        response = payload.get("response") if isinstance(payload, dict) else None
        return response if isinstance(response, str) else ""

    async def _record_health(self, provider: AIProvider, model: AIModel, *, status: str, metadata: dict[str, object]) -> None:
        await self.repository.record_health(
            ProviderHealth(
                provider_id=provider.id,
                model_id=model.id,
                status=status,
                latency_ms=0,
                memory_usage_mb=None,
                gpu_usage_pct=None,
                request_queue_depth=0,
                error_rate=0.0,
                token_usage=0,
                health_metadata=metadata,
            )
        )

    async def _cache_get(self, key: str):
        if self.redis_client is None:
            return None
        raw = await self.redis_client.get(key)
        return json.loads(raw) if raw else None

    async def _cache_set(self, key: str, value, ttl: int) -> None:
        if self.redis_client is None:
            return
        await self.redis_client.set(key, json.dumps(value), ex=ttl)

    async def _invalidate_catalog_cache(self) -> None:
        if self.redis_client is None:
            return
        await self.redis_client.delete("ai:models:list", "ai:providers:list", "ai:health:snapshot")
