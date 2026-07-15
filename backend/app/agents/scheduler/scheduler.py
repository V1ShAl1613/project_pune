"""Priority scheduler for agent tasks and workflows."""

from __future__ import annotations

import asyncio
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any
from uuid import UUID, uuid4


@dataclass(order=True, slots=True)
class ScheduledItem:
    """Internal priority queue item."""

    priority: int
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc), compare=False)
    task_id: UUID = field(default_factory=uuid4, compare=False)
    payload: dict[str, Any] = field(default_factory=dict, compare=False)


class AgentScheduler:
    """Priority queue scheduler for tasks and workflows."""

    def __init__(self) -> None:
        self._queue: asyncio.PriorityQueue[ScheduledItem] = asyncio.PriorityQueue()

    async def schedule(self, *, priority: int, payload: dict[str, Any]) -> UUID:
        item = ScheduledItem(priority=-priority, payload=payload)
        await self._queue.put(item)
        return item.task_id

    async def next_item(self) -> ScheduledItem:
        return await self._queue.get()

    def size(self) -> int:
        return self._queue.qsize()
