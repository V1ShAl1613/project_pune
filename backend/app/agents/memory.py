"""Memory interfaces for short-term, session, shared, and vector memory."""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any


class MemoryStore(ABC):
    """Abstract memory provider used by agents and orchestrators."""

    @abstractmethod
    async def get(self, key: str) -> Any | None:
        raise NotImplementedError

    @abstractmethod
    async def set(self, key: str, value: Any, ttl_seconds: int | None = None) -> None:
        raise NotImplementedError

    @abstractmethod
    async def delete(self, key: str) -> None:
        raise NotImplementedError

    @abstractmethod
    async def cleanup(self) -> int:
        raise NotImplementedError


@dataclass(slots=True)
class InMemoryStore(MemoryStore):
    """Simple local memory store used for tests and fallbacks."""

    values: dict[str, Any] = field(default_factory=dict)

    async def get(self, key: str) -> Any | None:
        return self.values.get(key)

    async def set(self, key: str, value: Any, ttl_seconds: int | None = None) -> None:
        self.values[key] = value

    async def delete(self, key: str) -> None:
        self.values.pop(key, None)

    async def cleanup(self) -> int:
        size = len(self.values)
        self.values.clear()
        return size


@dataclass(slots=True)
class MemoryManager:
    """Coordinates the memory stores used by the runtime."""

    short_term: MemoryStore = field(default_factory=InMemoryStore)
    long_term: MemoryStore = field(default_factory=InMemoryStore)
    vector: MemoryStore = field(default_factory=InMemoryStore)
    session: MemoryStore = field(default_factory=InMemoryStore)
    shared: MemoryStore = field(default_factory=InMemoryStore)
    working: MemoryStore = field(default_factory=InMemoryStore)

    async def cleanup(self) -> dict[str, int]:
        return {
            "short_term": await self.short_term.cleanup(),
            "long_term": await self.long_term.cleanup(),
            "vector": await self.vector.cleanup(),
            "session": await self.session.cleanup(),
            "shared": await self.shared.cleanup(),
            "working": await self.working.cleanup(),
        }
