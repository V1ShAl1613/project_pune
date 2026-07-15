from __future__ import annotations

from types import SimpleNamespace

import pytest

from app.database.services import seed_service
from app.database.services.seed_service import SeedService


class FakeRepository:
    def __init__(self) -> None:
        self.entities: list[object] = []

    async def exists(self, filters: dict[str, object]) -> bool:
        for entity in self.entities:
            if all(getattr(entity, key) == value for key, value in filters.items()):
                return True
        return False

    async def create(self, entity):
        self.entities.append(entity)
        return entity


class FakeRepositoryFactory:
    instances: list["FakeRepositoryFactory"] = []

    def __init__(self, session) -> None:
        self.session = session
        self.repositories: dict[type[object], FakeRepository] = {}
        FakeRepositoryFactory.instances.append(self)

    def create(self, model):
        return self.repositories.setdefault(model, FakeRepository())


class FakeSession:
    async def commit(self) -> None:
        return None


@pytest.mark.asyncio
async def test_seed_service_loads_and_applies_fixture(monkeypatch) -> None:
    FakeRepositoryFactory.instances.clear()
    monkeypatch.setattr(seed_service, "RepositoryFactory", FakeRepositoryFactory)

    service = SeedService()
    result = await service.seed(FakeSession())

    assert result["organizations"] == 1
    assert result["departments"] == 1
    assert result["teams"] == 1
    assert result["permissions"] == 2
    assert result["roles"] == 1
    assert result["role_permissions"] == 2

    factory = FakeRepositoryFactory.instances[0]
    department_repo = factory.repositories[next(model for model in factory.repositories if model.__name__ == "Department")]
    department = department_repo.entities[0]
    assert department.organization_id is not None
