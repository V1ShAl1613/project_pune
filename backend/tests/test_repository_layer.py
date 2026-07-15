from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock

import pytest

from app.database.models.organization import Organization
from app.database.repositories.base import CRUDRepository, PaginationParams, SortOrder


@pytest.mark.asyncio
async def test_crud_repository_create_and_soft_delete() -> None:
    session = AsyncMock()
    session.add = MagicMock()
    session.flush = AsyncMock()
    session.delete = AsyncMock()
    repository = CRUDRepository(session, Organization)
    entity = Organization(code="platform", name="Platform", status="active")

    created = await repository.create(entity)
    assert created is entity
    session.add.assert_called_once_with(entity)

    deleted = await repository.soft_delete(entity)
    assert deleted.is_deleted is True


@pytest.mark.asyncio
async def test_crud_repository_paginate_and_exists() -> None:
    session = AsyncMock()
    repository = CRUDRepository(session, Organization)
    entity = Organization(code="platform", name="Platform", status="active")

    result = MagicMock()
    result.scalars.return_value.unique.return_value.all.return_value = [entity]
    count_result = MagicMock()
    count_result.scalar_one.return_value = 1
    session.execute = AsyncMock(side_effect=[result, count_result, result])

    page = await repository.paginate(
        PaginationParams(page=1, page_size=10),
        filters={"status": "active"},
        sort=SortOrder(field_name="name"),
        search="Plat",
        search_fields=["name"],
    )

    assert page.total == 1
    assert page.items == [entity]

    exists = await repository.exists({"code": "platform"})
    assert exists is True
