from __future__ import annotations

from collections.abc import AsyncIterator, Mapping, Sequence
from contextlib import asynccontextmanager
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any, Generic, TypeVar, cast

from sqlalchemy import Select, and_, asc, delete, desc, func, or_, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.models.base import BaseModel as DatabaseBaseModel

EntityT = TypeVar("EntityT", bound=DatabaseBaseModel)


@dataclass(slots=True)
class PaginationParams:
    """Pagination arguments for repository queries."""

    page: int = 1
    page_size: int = 50

    @property
    def offset(self) -> int:
        return max(0, (self.page - 1) * self.page_size)


@dataclass(slots=True)
class SortOrder:
    """Sort direction for repository queries."""

    field_name: str
    descending: bool = False


@dataclass(slots=True)
class Page(Generic[EntityT]):
    """Paginated repository response."""

    items: Sequence[EntityT]
    total: int
    page: int
    page_size: int


class BaseRepository(Generic[EntityT]):
    """Shared async query helpers for mapped entities."""

    def __init__(self, session: AsyncSession, model: type[EntityT]) -> None:
        self.session = session
        self.model = model

    @asynccontextmanager
    async def transaction(self) -> AsyncIterator[AsyncSession]:
        if self.session.in_transaction():
            async with self.session.begin_nested():
                yield self.session
            tx = self.session.get_transaction()
            if tx is not None and not tx.nested:
                await self.session.commit()
        else:
            async with self.session.begin():
                yield self.session

    async def get_by_id(self, identifier: Any) -> EntityT | None:
        return await self.session.get(self.model, identifier)

    async def list_all(self) -> Sequence[EntityT]:
        result = await self.session.execute(select(self.model))
        return result.scalars().unique().all()

    async def count(self, filters: Mapping[str, Any] | None = None) -> int:
        statement = select(func.count()).select_from(self.model)
        statement = self._apply_filters(statement, filters)
        result = await self.session.execute(statement)
        return int(result.scalar_one())

    async def exists(self, filters: Mapping[str, Any]) -> bool:
        statement = select(self.model)
        statement = self._apply_filters(statement, filters).limit(1)
        result = await self.session.execute(statement)
        return result.scalar_one_or_none() is not None

    async def paginate(
        self,
        pagination: PaginationParams,
        *,
        filters: Mapping[str, Any] | None = None,
        sort: SortOrder | None = None,
        search: str | None = None,
        search_fields: Sequence[str] | None = None,
    ) -> Page[EntityT]:
        statement = select(self.model)
        statement = self._apply_filters(statement, filters)
        statement = self._apply_search(statement, search, search_fields)
        statement = self._apply_sort(statement, sort)

        count_statement = select(func.count()).select_from(self.model)
        count_statement = self._apply_filters(count_statement, filters)
        count_statement = self._apply_search(count_statement, search, search_fields)

        result = await self.session.execute(statement.limit(pagination.page_size).offset(pagination.offset))
        total_result = await self.session.execute(count_statement)
        return Page(
            items=result.scalars().unique().all(),
            total=int(total_result.scalar_one()),
            page=pagination.page,
            page_size=pagination.page_size,
        )

    async def bulk_insert(self, entities: Sequence[EntityT]) -> Sequence[EntityT]:
        self.session.add_all(list(entities))
        await self.session.flush()
        return entities

    async def bulk_update(
        self,
        records: Sequence[Mapping[str, Any]],
        *,
        identifier_field: str = "id",
    ) -> int:
        updated = 0
        for record in records:
            identifier = record[identifier_field]
            values = {key: value for key, value in record.items() if key != identifier_field}
            statement = update(self.model).where(getattr(self.model, identifier_field) == identifier).values(**values)
            result = await self.session.execute(statement)
            updated += int(result.rowcount or 0)
        await self.session.flush()
        return updated

    def _apply_filters(self, statement: Select[Any], filters: Mapping[str, Any] | None) -> Select[Any]:
        if not filters:
            return statement
        expressions = [getattr(self.model, key) == value for key, value in filters.items() if hasattr(self.model, key)]
        if not expressions:
            return statement
        return statement.where(and_(*expressions))

    def _apply_search(
        self,
        statement: Select[Any],
        search: str | None,
        search_fields: Sequence[str] | None,
    ) -> Select[Any]:
        if not search or not search_fields:
            return statement
        terms = [getattr(self.model, field).ilike(f"%{search}%") for field in search_fields if hasattr(self.model, field)]
        if not terms:
            return statement
        return statement.where(or_(*terms))

    def _apply_sort(self, statement: Select[Any], sort: SortOrder | None) -> Select[Any]:
        if sort is None or not hasattr(self.model, sort.field_name):
            return statement
        column = getattr(self.model, sort.field_name)
        return statement.order_by(desc(column) if sort.descending else asc(column))


class CRUDRepository(BaseRepository[EntityT]):
    """Repository with create, update, delete, soft-delete, and restore operations."""

    async def create(self, entity: EntityT) -> EntityT:
        self.session.add(entity)
        await self.session.flush()
        return entity

    async def update(self, entity: EntityT, values: Mapping[str, Any]) -> EntityT:
        for key, value in values.items():
            if hasattr(entity, key):
                setattr(entity, key, value)
        await self.session.flush()
        return entity

    async def delete(self, entity: EntityT) -> None:
        await self.session.delete(entity)

    async def soft_delete(self, entity: EntityT) -> EntityT:
        if hasattr(entity, "mark_deleted"):
            entity.mark_deleted()
        else:
            setattr(entity, "deleted_at", datetime.now(timezone.utc))
        await self.session.flush()
        return entity

    async def restore(self, entity: EntityT) -> EntityT:
        if hasattr(entity, "restore"):
            entity.restore()
        else:
            setattr(entity, "deleted_at", None)
        await self.session.flush()
        return entity
