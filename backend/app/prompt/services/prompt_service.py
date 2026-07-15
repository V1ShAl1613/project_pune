from __future__ import annotations

import hashlib
import json
import logging
from dataclasses import dataclass
from datetime import UTC, datetime, timedelta
from uuid import uuid4

from redis.asyncio import Redis

from app.ai.clients.ollama_client import OllamaClient
from app.core.settings import AppSettings
from app.exceptions.base import BaseApplicationException
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
from app.prompt.repositories.prompt_repository import PromptRepository
from app.prompt.schemas import (
    PromptApprovalResponse,
    PromptCategoryCreateRequest,
    PromptCategoryResponse,
    PromptCreateRequest,
    PromptExecuteRequest,
    PromptExecutionResponse,
    PromptLifecycleStatus,
    PromptPolicyResponse,
    PromptPublishRequest,
    PromptResponse,
    PromptRollbackRequest,
    PromptTemplateResponse,
    PromptValidateRequest,
    PromptValidationResponse,
    PromptVariableResponse,
    PromptVersionResponse,
)
from app.prompt.utils.renderer import PromptRenderer
from app.prompt.utils.security import PromptSecurityEngine
from app.prompt.utils.validation import PromptValidationEngine


@dataclass(slots=True)
class PromptService:
    """Enterprise prompt registry, versioning, validation, and execution service."""

    repository: PromptRepository
    settings: AppSettings
    ollama_client: OllamaClient
    redis_client: Redis | None
    logger: logging.Logger

    def __post_init__(self) -> None:
        self.renderer = PromptRenderer()
        self.security = PromptSecurityEngine(
            forbidden_keywords=tuple(self.settings.prompt_forbidden_keywords),
            secret_patterns=tuple(self.settings.prompt_sensitive_patterns),
        )
        self.validator = PromptValidationEngine(renderer=self.renderer, security=self.security)

    async def list_categories(self) -> list[PromptCategoryResponse]:
        await self._seed_default_categories()
        cached = await self._cache_get("prompt:categories:list")
        if cached:
            return [PromptCategoryResponse.model_validate(item) for item in cached]
        categories = await self.repository.list_categories()
        payload = [PromptCategoryResponse.model_validate(category, from_attributes=True).model_dump(mode="json") for category in categories]
        await self._cache_set("prompt:categories:list", payload, ttl=self.settings.prompt_registry_cache_ttl_seconds)
        return [PromptCategoryResponse.model_validate(item) for item in payload]

    async def list_prompts(self, search: str | None = None, status: str | None = None, category_code: str | None = None) -> list[PromptResponse]:
        await self._seed_default_categories()
        cached = await self._cache_get(self._registry_cache_key(search, status, category_code))
        if cached:
            return [PromptResponse.model_validate(item) for item in cached]
        prompts = await self.repository.list_prompts(search=search, status=status, category_code=category_code)
        payload = [self._serialize_prompt(prompt).model_dump(mode="json") for prompt in prompts]
        await self._cache_set(self._registry_cache_key(search, status, category_code), payload, ttl=self.settings.prompt_cache_ttl_seconds)
        return [PromptResponse.model_validate(item) for item in payload]

    async def get_prompt(self, prompt_id) -> PromptResponse:
        prompt = await self.repository.get_prompt(prompt_id)
        if prompt is None:
            raise BaseApplicationException("Prompt not found", status_code=404, error_code="prompt_not_found")
        return self._serialize_prompt(prompt)

    async def create_prompt(self, request: PromptCreateRequest) -> PromptResponse:
        category = await self._resolve_category(request.category_code)
        if await self.repository.get_prompt_by_code(request.code) is not None:
            raise BaseApplicationException("Prompt already exists", status_code=409, error_code="prompt_conflict")

        prompt = Prompt(
            category_id=category.id if category else None,
            code=request.code,
            name=request.name,
            description=request.description,
            owner_type=request.owner_type,
            owner_id=request.owner_id,
            status=request.status.value,
            labels=request.labels,
            tags=request.tags,
            prompt_metadata=request.metadata,
        )
        template = PromptTemplate(
            prompt=prompt,
            template_type=request.template.template_type.value,
            template_format=request.template.template_format,
            content=self._sanitize_template(request.template.content),
            compiled_content=None,
            status="active",
            is_active=True,
            template_metadata=request.template.metadata,
        )
        version = self._build_version(prompt, request.template.content, version_number=1, status=PromptLifecycleStatus.DRAFT.value)
        async with self.repository.transaction():
            created = await self.repository.create_prompt(prompt)
            await self.repository.create_template(template)
            await self.repository.create_version(version)
            await self._sync_variables(created, request.variables)
            await self._sync_policies(created, request.policies)
            await self._audit(created.id, "prompt_created", after=self._serialize_prompt(created).model_dump(mode="json"))
        await self._invalidate_caches()
        return await self.get_prompt(created.id)

    async def update_prompt(self, prompt_id, request) -> PromptResponse:
        prompt = await self.repository.get_prompt(prompt_id)
        if prompt is None:
            raise BaseApplicationException("Prompt not found", status_code=404, error_code="prompt_not_found")
        before = self._serialize_prompt(prompt).model_dump(mode="json")
        updates = request.model_dump(exclude_none=True)
        category = await self._resolve_category(updates.pop("category_code", None)) if "category_code" in updates else None
        if category is not None:
            updates["category_id"] = category.id
        template_request = updates.pop("template", None)
        variables = updates.pop("variables", None)
        policies = updates.pop("policies", None)
        if "labels" in updates and updates["labels"] is not None:
            updates["labels"] = [item.strip() for item in updates["labels"] if item and item.strip()]
        if "tags" in updates and updates["tags"] is not None:
            updates["tags"] = [item.strip() for item in updates["tags"] if item and item.strip()]
        async with self.repository.transaction():
            await self.repository.update_prompt(prompt, updates)
            if template_request is not None:
                await self._replace_template(prompt.id, template_request)
            if variables is not None:
                await self._sync_variables(prompt, variables)
            if policies is not None:
                await self._sync_policies(prompt, policies)
            await self._audit(prompt.id, "prompt_updated", before=before, after=self._serialize_prompt(prompt).model_dump(mode="json"))
        await self._invalidate_caches()
        return await self.get_prompt(prompt.id)

    async def delete_prompt(self, prompt_id) -> None:
        prompt = await self.repository.get_prompt(prompt_id)
        if prompt is None:
            raise BaseApplicationException("Prompt not found", status_code=404, error_code="prompt_not_found")
        before = self._serialize_prompt(prompt).model_dump(mode="json")
        async with self.repository.transaction():
            await self.repository.delete_prompt(prompt)
            await self._audit(prompt.id, "prompt_deleted", before=before, after=self._serialize_prompt(prompt).model_dump(mode="json"))
        await self._invalidate_caches()

    async def publish_prompt(self, prompt_id, request: PromptPublishRequest) -> PromptResponse:
        prompt = await self.repository.get_prompt(prompt_id)
        if prompt is None:
            raise BaseApplicationException("Prompt not found", status_code=404, error_code="prompt_not_found")
        latest = await self._latest_version(prompt.id)
        if latest is None:
            raise BaseApplicationException("Prompt has no version to publish", status_code=409, error_code="prompt_version_missing")
        latest.status = PromptLifecycleStatus.PUBLISHED.value
        latest.approval_status = "approved"
        approval = PromptApproval(
            prompt_id=prompt.id,
            version_id=latest.id,
            approver=request.approver,
            status="approved",
            comment=request.comment,
            approval_metadata=request.metadata,
        )
        async with self.repository.transaction():
            prompt.status = PromptLifecycleStatus.PUBLISHED.value
            await self.repository.add_approval(approval)
            await self.repository.add_audit(
                PromptAudit(
                    prompt_id=prompt.id,
                    version_id=latest.id,
                    action="prompt_published",
                    actor=request.approver,
                    before_state={"status": PromptLifecycleStatus.DRAFT.value},
                    after_state={"status": PromptLifecycleStatus.PUBLISHED.value, "version_id": str(latest.id)},
                    audit_metadata=request.metadata,
                )
            )
        await self._invalidate_caches()
        return await self.get_prompt(prompt.id)

    async def rollback_prompt(self, prompt_id, request: PromptRollbackRequest) -> PromptResponse:
        prompt = await self.repository.get_prompt(prompt_id)
        if prompt is None:
            raise BaseApplicationException("Prompt not found", status_code=404, error_code="prompt_not_found")
        target_version = await self.repository.get_version(request.version_id)
        if target_version is None or target_version.prompt_id != prompt.id:
            raise BaseApplicationException("Version not found", status_code=404, error_code="prompt_version_not_found")
        latest_version_number = await self._next_version_number(prompt.id)
        rollback_version = PromptVersion(
            prompt_id=prompt.id,
            version_number=latest_version_number,
            status=PromptLifecycleStatus.DRAFT.value,
            approval_status="rollback",
            rollback_from_version_id=target_version.id,
            checksum=self._checksum(target_version.content),
            content=target_version.content,
            rendered_content=target_version.rendered_content,
            version_metadata={**target_version.version_metadata, **request.metadata, "rollback": True, "rollback_comment": request.comment},
        )
        async with self.repository.transaction():
            prompt.status = PromptLifecycleStatus.DRAFT.value
            await self.repository.create_version(rollback_version)
            await self.repository.add_audit(
                PromptAudit(
                    prompt_id=prompt.id,
                    version_id=rollback_version.id,
                    action="prompt_rollback",
                    actor=request.comment,
                    before_state={"version_id": str(target_version.id)},
                    after_state={"version_id": str(rollback_version.id)},
                    audit_metadata=request.metadata,
                )
            )
        await self._invalidate_caches()
        return await self.get_prompt(prompt.id)

    async def validate_prompt(self, prompt_id: UUID | None, request: PromptValidateRequest) -> PromptValidationResponse:
        prompt = await self.repository.get_prompt(prompt_id) if prompt_id is not None else None
        if prompt_id is not None and prompt is None:
            raise BaseApplicationException("Prompt not found", status_code=404, error_code="prompt_not_found")
        template = request.template.content if request.template is not None else await self._resolve_template_content(prompt)
        required_variables = [variable.name for variable in prompt.variables if variable.required] if prompt is not None else None
        response = self.validator.validate(
            template,
            variables=request.variables,
            context=request.context,
            output_format=request.output_format,
            max_length=request.max_length or self.settings.prompt_max_length,
            required_variables=required_variables,
        )
        response.prompt_id = prompt_id
        if prompt is not None:
            response.version_id = (await self._latest_version(prompt.id)).id if await self._latest_version(prompt.id) is not None else None
        await self._cache_set(self._validation_cache_key(prompt_id), response.model_dump(mode="json"), ttl=self.settings.prompt_validation_cache_ttl_seconds)
        await self._audit(prompt_id, "prompt_validated", after=response.model_dump(mode="json"))
        return response

    async def execute_prompt(self, prompt_id: UUID, request: PromptExecuteRequest):
        prompt = await self.repository.get_prompt(prompt_id)
        if prompt is None:
            raise BaseApplicationException("Prompt not found", status_code=404, error_code="prompt_not_found")
        version = await self.repository.get_version(request.version_id) if request.version_id is not None else await self._latest_version(prompt.id)
        if version is None:
            raise BaseApplicationException("Prompt version not found", status_code=404, error_code="prompt_version_not_found")
        rendered_prompt = self.renderer.render(version.content, {**request.context, **request.variables})
        validation = self.validator.validate(
            version.content,
            variables=request.variables,
            context=request.context,
            output_format=request.response_format,
            max_length=self.settings.prompt_max_length,
            required_variables=[variable.name for variable in prompt.variables if variable.required],
        )
        if not validation.is_valid and self.settings.prompt_enable_policy_enforcement:
            raise BaseApplicationException("Prompt validation failed", status_code=422, error_code="prompt_validation_failed")
        model_name = request.model_name or self.settings.ai_default_model
        provider_name = request.provider_name or self.settings.ai_default_provider
        execution = PromptExecution(
            prompt_id=prompt.id,
            version_id=version.id,
            model_name=model_name,
            provider_name=provider_name,
            status="success",
            stream_enabled=request.stream,
            input_variables=request.variables,
            rendered_prompt=rendered_prompt,
            output_text="",
            input_metadata=request.metadata,
            output_metadata={},
            execution_metadata={"context": request.context, "response_format": request.response_format},
            tokens_in=self.validator.estimate_tokens(rendered_prompt),
            tokens_out=0,
            latency_ms=0,
        )
        start = datetime.now(UTC)
        if request.stream:
            async def stream_execution():
                response_text = ""
                async for chunk in self.ollama_client.stream_chat(
                    model=model_name,
                    messages=[{"role": "user", "content": rendered_prompt}],
                    options=self._build_options(request.temperature, request.top_p, request.max_tokens),
                ):
                    response_text += chunk
                    yield f"data: {json.dumps({'prompt_id': str(prompt.id), 'version_id': str(version.id), 'chunk': chunk, 'done': False})}\n\n"
                execution.output_text = response_text
                execution.tokens_out = self.validator.estimate_tokens(response_text)
                execution.latency_ms = self._elapsed_ms(start)
                await self.repository.add_execution(execution)
                await self._record_execution_analytics(prompt.id, version.id, execution)
                await self._audit(prompt.id, "prompt_executed", after=self._serialize_execution(execution))
                yield f"data: {json.dumps({'prompt_id': str(prompt.id), 'version_id': str(version.id), 'chunk': '', 'done': True})}\n\n"

            return stream_execution()

        result = await self.ollama_client.generate(
            model=model_name,
            prompt=rendered_prompt,
            options=self._build_options(request.temperature, request.top_p, request.max_tokens),
        )
        output_text = result.get("response", "") if isinstance(result, dict) else ""
        execution.output_text = output_text
        execution.tokens_out = self.validator.estimate_tokens(output_text)
        execution.latency_ms = self._elapsed_ms(start)
        execution.output_metadata = {"raw": result}
        async with self.repository.transaction():
            await self.repository.add_execution(execution)
            await self._record_execution_analytics(prompt.id, version.id, execution)
            await self._audit(prompt.id, "prompt_executed", after=self._serialize_execution(execution))
        await self._cache_set(self._execution_cache_key(prompt.id), self._serialize_execution(execution), ttl=self.settings.prompt_execution_cache_ttl_seconds)
        return PromptExecutionResponse.model_validate(execution, from_attributes=True)

    async def analytics(self) -> list[PromptAnalyticsResponse]:
        cached = await self._cache_get("prompt:analytics:snapshot")
        if cached:
            return [PromptAnalyticsResponse.model_validate(item) for item in cached]
        analytics_rows = await self.repository.list_analytics()
        payload = [PromptAnalyticsResponse.model_validate(row, from_attributes=True).model_dump(mode="json") for row in analytics_rows]
        await self._cache_set("prompt:analytics:snapshot", payload, ttl=self.settings.prompt_analytics_cache_ttl_seconds)
        return [PromptAnalyticsResponse.model_validate(item) for item in payload]

    async def seed_default_catalog(self) -> None:
        await self._seed_default_categories()

    async def _seed_default_categories(self) -> None:
        defaults = [
            ("threat-analysis", "Threat Analysis"),
            ("fraud-detection", "Fraud Detection"),
            ("executive-summary", "Executive Summary"),
            ("investigation", "Investigation"),
            ("compliance", "Compliance"),
            ("incident-response", "Incident Response"),
            ("risk-assessment", "Risk Assessment"),
            ("knowledge-retrieval", "Knowledge Retrieval"),
            ("report-generation", "Report Generation"),
            ("classification", "Classification"),
            ("conversation", "Conversation"),
            ("general", "General"),
        ]
        async with self.repository.transaction():
            existing = {category.code for category in await self.repository.list_categories()}
            for code, name in defaults:
                if code not in existing:
                    await self.repository.upsert_category(code=code, name=name, description=f"{name} prompt category", status="active", metadata={"seeded": True})
        await self._invalidate_caches()

    async def _resolve_category(self, category_code: str | None) -> PromptCategory | None:
        code = category_code or self.settings.prompt_default_category
        if code is None:
            return None
        category = await self.repository.get_category_by_code(code)
        if category is None:
            category = await self.repository.upsert_category(code=code, name=code.replace("-", " ").title(), description=f"{code} prompt category", status="active", metadata={"auto_created": True})
        return category

    async def _sync_variables(self, prompt: Prompt, variables) -> None:
        if variables is None:
            return
        prompt.variables.clear()
        for variable in variables:
            await self.repository.add_variable(
                PromptVariable(
                    prompt_id=prompt.id,
                    name=variable.name,
                    variable_type=variable.variable_type.value,
                    scope=variable.scope,
                    source=variable.source,
                    required=variable.required,
                    default_value=variable.default_value,
                    is_secret=variable.is_secret,
                    mask_output=variable.mask_output,
                    description=variable.description,
                    variable_metadata=variable.metadata,
                )
            )

    async def _sync_policies(self, prompt: Prompt, policies) -> None:
        if policies is None:
            return
        prompt.policies.clear()
        for policy in policies:
            await self.repository.add_policy(
                PromptPolicy(
                    prompt_id=prompt.id,
                    scope=policy.scope.value,
                    policy_type=policy.policy_type,
                    is_enforced=policy.is_enforced,
                    status=policy.status,
                    policy_rules=policy.rules,
                    policy_metadata=policy.metadata,
                )
            )

    async def _replace_template(self, prompt_id, template_request) -> None:
        template = PromptTemplate(
            prompt_id=prompt_id,
            template_type=template_request.template_type.value,
            template_format=template_request.template_format,
            content=self._sanitize_template(template_request.content),
            compiled_content=None,
            status="active",
            is_active=True,
            template_metadata=template_request.metadata,
        )
        await self.repository.create_template(template)
        version = self._build_version(await self.repository.get_prompt(prompt_id), template_request.content, version_number=await self._next_version_number(prompt_id), status=PromptLifecycleStatus.DRAFT.value)
        await self.repository.create_version(version)

    def _serialize_prompt(self, prompt: Prompt) -> PromptResponse:
        return PromptResponse(
            id=prompt.id,
            category_id=prompt.category_id,
            code=prompt.code,
            name=prompt.name,
            description=prompt.description,
            owner_type=prompt.owner_type,
            owner_id=prompt.owner_id,
            status=prompt.status,
            labels=list(prompt.labels or []),
            tags=list(prompt.tags or []),
            archived_reason=prompt.archived_reason,
            prompt_metadata=prompt.prompt_metadata,
            created_at=prompt.created_at,
            updated_at=prompt.updated_at,
            category=PromptCategoryResponse.model_validate(prompt.category, from_attributes=True) if prompt.category else None,
            templates=[PromptTemplateResponse.model_validate(template, from_attributes=True) for template in prompt.templates],
            versions=[PromptVersionResponse.model_validate(version, from_attributes=True) for version in sorted(prompt.versions, key=lambda item: item.version_number)],
            variables=[PromptVariableResponse.model_validate(variable, from_attributes=True) for variable in prompt.variables],
            policies=[PromptPolicyResponse.model_validate(policy, from_attributes=True) for policy in prompt.policies],
            approvals=[PromptApprovalResponse.model_validate(approval, from_attributes=True) for approval in prompt.approvals],
        )

    def _serialize_execution(self, execution: PromptExecution) -> dict[str, object]:
        return PromptExecutionResponse.model_validate(execution, from_attributes=True).model_dump(mode="json")

    def _build_version(self, prompt: Prompt, content: str, *, version_number: int, status: str) -> PromptVersion:
        return PromptVersion(
            prompt_id=prompt.id,
            version_number=version_number,
            status=status,
            approval_status="draft",
            checksum=self._checksum(content),
            content=content,
            rendered_content=self.renderer.render(content, {}),
            version_metadata={"generated_at": datetime.now(UTC).isoformat()},
        )

    async def _latest_version(self, prompt_id) -> PromptVersion | None:
        versions = await self.repository.list_versions(prompt_id)
        return versions[0] if versions else None

    async def _next_version_number(self, prompt_id) -> int:
        versions = await self.repository.list_versions(prompt_id)
        return (versions[0].version_number if versions else 0) + 1

    async def _resolve_template_content(self, prompt: Prompt | None) -> str:
        if prompt is None or not prompt.templates:
            return ""
        return prompt.templates[0].content

    def _sanitize_template(self, content: str) -> str:
        sanitized = self.security.sanitize_text(content)
        if self.settings.prompt_enable_secret_masking:
            sanitized = self.security.mask_secrets(sanitized)
        return sanitized

    async def _record_execution_analytics(self, prompt_id, version_id, execution: PromptExecution) -> None:
        await self.repository.add_analytics(
            PromptAnalytics(
                prompt_id=prompt_id,
                version_id=version_id,
                metric_name="execution_count",
                metric_value=1.0,
                dimension_data={"model": execution.model_name, "provider": execution.provider_name},
                analytics_metadata={"execution_id": str(execution.id)},
            )
        )
        await self.repository.add_analytics(
            PromptAnalytics(
                prompt_id=prompt_id,
                version_id=version_id,
                metric_name="tokens_out",
                metric_value=float(execution.tokens_out),
                dimension_data={"model": execution.model_name},
                analytics_metadata={"execution_id": str(execution.id)},
            )
        )
        await self.repository.add_analytics(
            PromptAnalytics(
                prompt_id=prompt_id,
                version_id=version_id,
                metric_name="latency_ms",
                metric_value=float(execution.latency_ms),
                dimension_data={"model": execution.model_name},
                analytics_metadata={"execution_id": str(execution.id)},
            )
        )

    async def _audit(self, prompt_id, action: str, *, before: dict[str, object] | None = None, after: dict[str, object] | None = None) -> None:
        await self.repository.add_audit(
            PromptAudit(
                prompt_id=prompt_id,
                action=action,
                actor="system",
                before_state=before or {},
                after_state=after or {},
                audit_metadata={"service": "prompt"},
            )
        )

    async def _cache_get(self, key: str):
        if self.redis_client is None:
            return None
        payload = await self.redis_client.get(key)
        return json.loads(payload) if payload else None

    async def _cache_set(self, key: str, value, ttl: int) -> None:
        if self.redis_client is None:
            return
        await self.redis_client.set(key, json.dumps(value), ex=ttl)

    async def _invalidate_caches(self) -> None:
        if self.redis_client is None:
            return
        keys = ["prompt:categories:list", "prompt:analytics:snapshot"]
        await self.redis_client.delete(*keys)

    def _registry_cache_key(self, search: str | None, status: str | None, category_code: str | None) -> str:
        return f"prompt:registry:{search or '*'}:{status or '*'}:{category_code or '*'}"

    def _validation_cache_key(self, prompt_id) -> str:
        return f"prompt:validation:{prompt_id or 'global'}"

    def _execution_cache_key(self, prompt_id) -> str:
        return f"prompt:execution:{prompt_id}"

    def _checksum(self, content: str) -> str:
        return hashlib.sha256(content.encode("utf-8")).hexdigest()

    def _elapsed_ms(self, started_at: datetime) -> int:
        return max(0, int((datetime.now(UTC) - started_at).total_seconds() * 1000))
