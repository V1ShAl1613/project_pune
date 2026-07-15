from __future__ import annotations

from dataclasses import dataclass
from uuid import UUID

from redis.asyncio import Redis

from app.authorization.models import AuthorizationContext, AuthorizationDecision
from app.auth.utils.serialization import from_json, to_json


@dataclass(slots=True)
class AuthorizationCacheRepository:
    redis_client: Redis

    def _roles_key(self, user_id: UUID) -> str:
        return f"authorization:roles:{user_id}"

    def _permissions_key(self, user_id: UUID) -> str:
        return f"authorization:permissions:{user_id}"

    def _context_key(self, user_id: UUID) -> str:
        return f"authorization:context:{user_id}"

    def _policy_key(self, code: str) -> str:
        return f"authorization:policy:{code}"

    async def cache_context(self, context: AuthorizationContext, ttl_seconds: int) -> None:
        payload = {
            "user_id": str(context.user_id),
            "session_id": str(context.session_id),
            "role_codes": sorted(context.role_codes),
            "permission_codes": sorted(context.permission_codes),
            "policy_codes": sorted(context.policy_codes),
            "is_super_admin": context.is_super_admin,
        }
        await self.redis_client.setex(self._context_key(context.user_id), ttl_seconds, to_json(payload))

    async def get_context(self, user_id: UUID) -> AuthorizationContext | None:
        value = await self.redis_client.get(self._context_key(user_id))
        if value is None:
            return None
        payload = from_json(value)
        return AuthorizationContext(
            user_id=UUID(str(payload["user_id"])),
            session_id=UUID(str(payload["session_id"])),
            role_codes=set(payload.get("role_codes", [])),
            permission_codes=set(payload.get("permission_codes", [])),
            policy_codes=set(payload.get("policy_codes", [])),
            is_super_admin=bool(payload.get("is_super_admin", False)),
        )

    async def cache_permissions(self, user_id: UUID, permissions: list[str], ttl_seconds: int) -> None:
        await self.redis_client.setex(self._permissions_key(user_id), ttl_seconds, to_json(sorted(set(permissions))))

    async def get_permissions(self, user_id: UUID) -> list[str] | None:
        value = await self.redis_client.get(self._permissions_key(user_id))
        if value is None:
            return None
        return list(from_json(value))

    async def cache_roles(self, user_id: UUID, roles: list[str], ttl_seconds: int) -> None:
        await self.redis_client.setex(self._roles_key(user_id), ttl_seconds, to_json(sorted(set(roles))))

    async def get_roles(self, user_id: UUID) -> list[str] | None:
        value = await self.redis_client.get(self._roles_key(user_id))
        if value is None:
            return None
        return list(from_json(value))

    async def cache_policy(self, code: str, policy: dict[str, object], ttl_seconds: int) -> None:
        await self.redis_client.setex(self._policy_key(code), ttl_seconds, to_json(policy))

    async def get_policy(self, code: str) -> dict[str, object] | None:
        value = await self.redis_client.get(self._policy_key(code))
        if value is None:
            return None
        return from_json(value)

    async def invalidate_user(self, user_id: UUID) -> None:
        await self.redis_client.delete(self._context_key(user_id), self._permissions_key(user_id), self._roles_key(user_id))

    async def invalidate_all(self) -> None:
        keys: list[str] = []
        async for key in self.redis_client.scan_iter(match="authorization:*"):
            keys.append(key)
        if keys:
            await self.redis_client.delete(*keys)

