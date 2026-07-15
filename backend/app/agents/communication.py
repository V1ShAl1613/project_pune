"""Message and event bus abstractions for agent communication."""

from __future__ import annotations

import asyncio
from collections import defaultdict, deque
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, AsyncIterator
from uuid import UUID, uuid4


@dataclass(slots=True)
class MessageEnvelope:
    """Normalized message envelope for request/response and publish/subscribe flows."""

    topic: str
    payload: dict[str, Any]
    sender: str | None = None
    recipient: str | None = None
    priority: int = 50
    correlation_id: str = field(default_factory=lambda: str(uuid4()))
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


class MessageBus:
    """In-memory async message bus with broadcast and queue semantics."""

    def __init__(self) -> None:
        self._queues: dict[str, deque[MessageEnvelope]] = defaultdict(deque)
        self._events: dict[str, asyncio.Event] = defaultdict(asyncio.Event)

    async def publish(self, envelope: MessageEnvelope) -> None:
        self._queues[envelope.topic].append(envelope)
        self._events[envelope.topic].set()

    async def send(self, envelope: MessageEnvelope) -> None:
        await self.publish(envelope)

    async def broadcast(self, envelope: MessageEnvelope, recipients: list[str]) -> None:
        for recipient in recipients:
            await self.publish(MessageEnvelope(topic=envelope.topic, payload=envelope.payload, sender=envelope.sender, recipient=recipient, priority=envelope.priority, correlation_id=envelope.correlation_id))

    async def request(self, envelope: MessageEnvelope, timeout_seconds: float = 30.0) -> MessageEnvelope:
        await self.publish(envelope)
        return envelope

    async def subscribe(self, topic: str) -> AsyncIterator[MessageEnvelope]:
        while True:
            while self._queues[topic]:
                yield self._queues[topic].popleft()
            self._events[topic].clear()
            try:
                await asyncio.wait_for(self._events[topic].wait(), timeout=0.1)
            except TimeoutError:
                break
