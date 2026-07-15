from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC, datetime, timedelta

from redis.asyncio import Redis

from app.auth.tokens.service import JwtService
from app.auth.utils.serialization import from_json, to_json


@dataclass(slots=True)
class TokenRepository:
    redis_client: Redis
    jwt_service: JwtService

    async def store_refresh_token(self, token_hash: str, payload: dict[str, object], ttl_seconds: int) -> None:
        await self.redis_client.setex(self._refresh_key(token_hash), ttl_seconds, to_json(payload))

    async def get_refresh_token(self, token_hash: str) -> dict[str, object] | None:
        value = await self.redis_client.get(self._refresh_key(token_hash))
        return from_json(value)

    async def revoke_refresh_token(self, token_hash: str, ttl_seconds: int) -> None:
        await self.redis_client.setex(self._refresh_revoked_key(token_hash), ttl_seconds, "1")

    async def is_refresh_token_revoked(self, token_hash: str) -> bool:
        value = await self.redis_client.get(self._refresh_revoked_key(token_hash))
        return value is not None

    async def store_session(self, session_id: str, payload: dict[str, object], ttl_seconds: int) -> None:
        await self.redis_client.setex(self._session_key(session_id), ttl_seconds, to_json(payload))

    async def get_session(self, session_id: str) -> dict[str, object] | None:
        value = await self.redis_client.get(self._session_key(session_id))
        return from_json(value)

    async def revoke_session(self, session_id: str, ttl_seconds: int) -> None:
        await self.redis_client.setex(self._session_revoked_key(session_id), ttl_seconds, "1")

    async def is_session_revoked(self, session_id: str) -> bool:
        value = await self.redis_client.get(self._session_revoked_key(session_id))
        return value is not None

    async def increment_failed_login(self, identifier: str, ttl_seconds: int) -> int:
        key = self._failed_login_key(identifier)
        count = await self.redis_client.incr(key)
        await self.redis_client.expire(key, ttl_seconds)
        return count

    async def reset_failed_login(self, identifier: str) -> None:
        await self.redis_client.delete(self._failed_login_key(identifier))
        await self.redis_client.delete(self._lock_key(identifier))

    async def get_failed_login_count(self, identifier: str) -> int:
        value = await self.redis_client.get(self._failed_login_key(identifier))
        return int(value or 0)

    async def lock_account(self, identifier: str, ttl_seconds: int) -> None:
        await self.redis_client.setex(self._lock_key(identifier), ttl_seconds, "1")

    async def is_account_locked(self, identifier: str) -> bool:
        value = await self.redis_client.get(self._lock_key(identifier))
        return value is not None

    async def store_one_time_token(self, kind: str, token_hash: str, payload: dict[str, object], ttl_seconds: int) -> None:
        await self.redis_client.setex(self._one_time_key(kind, token_hash), ttl_seconds, to_json(payload))

    async def consume_one_time_token(self, kind: str, token_hash: str) -> dict[str, object] | None:
        key = self._one_time_key(kind, token_hash)
        value = await self.redis_client.get(key)
        if value is None:
            return None
        await self.redis_client.delete(key)
        return from_json(value)

    def _refresh_key(self, token_hash: str) -> str:
        return f"auth:refresh:{token_hash}"

    def _refresh_revoked_key(self, token_hash: str) -> str:
        return f"auth:refresh:revoked:{token_hash}"

    def _session_key(self, session_id: str) -> str:
        return f"auth:session:{session_id}"

    def _session_revoked_key(self, session_id: str) -> str:
        return f"auth:session:revoked:{session_id}"

    def _failed_login_key(self, identifier: str) -> str:
        return f"auth:failed:{identifier}"

    def _lock_key(self, identifier: str) -> str:
        return f"auth:lock:{identifier}"

    def _one_time_key(self, kind: str, token_hash: str) -> str:
        return f"auth:{kind}:{token_hash}"
