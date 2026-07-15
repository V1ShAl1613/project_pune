from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any
from uuid import uuid4

from sqlalchemy.ext.asyncio import AsyncSession

from app.database.models import Department, FeatureFlag, Organization, Permission, Role, RolePermission, SystemSetting, Team
from app.database.repositories.factory import RepositoryFactory


@dataclass(slots=True)
class SeedService:
    """Loads and applies deterministic seed data from fixtures."""

    fixture_path: Path = field(default_factory=lambda: Path(__file__).resolve().parents[1] / "fixtures" / "core_seed.json")

    def load_seed_payload(self) -> dict[str, Any]:
        return json.loads(self.fixture_path.read_text(encoding="utf-8"))

    async def seed(self, session: AsyncSession) -> dict[str, int]:
        payload = self.load_seed_payload()
        repositories = RepositoryFactory(session)

        organization_map = await self._seed_organizations(repositories, payload.get("organizations", []))
        department_map = await self._seed_departments(repositories, payload.get("departments", []), organization_map)
        team_map = await self._seed_teams(repositories, payload.get("teams", []), department_map)
        permission_map = await self._seed_permissions(repositories, payload.get("permissions", []))
        role_map = await self._seed_roles(repositories, payload.get("roles", []), organization_map)
        role_permissions = await self._seed_role_permissions(session, payload.get("role_permissions", []), role_map, permission_map)

        inserted_counts = {
            "organizations": len(organization_map),
            "departments": len(department_map),
            "teams": len(team_map),
            "permissions": len(permission_map),
            "roles": len(role_map),
            "role_permissions": role_permissions,
            "system_settings": len(await self._seed_settings(repositories, payload.get("system_settings", []))),
            "feature_flags": len(await self._seed_feature_flags(repositories, payload.get("feature_flags", []))),
        }
        await session.commit()
        return inserted_counts

    async def _seed_organizations(
        self,
        repositories: RepositoryFactory,
        items: list[dict[str, Any]],
    ) -> dict[str, Any]:
        return await self._seed_entities(repositories, Organization, items, key_field="code")

    async def _seed_departments(
        self,
        repositories: RepositoryFactory,
        items: list[dict[str, Any]],
        organization_map: dict[str, Any],
    ) -> dict[str, Any]:
        prepared_items = []
        for item in items:
            prepared_items.append({
                **item,
                "organization_id": organization_map[item["organization_code"]],
            })
        return await self._seed_entities(repositories, Department, prepared_items, key_field="code")

    async def _seed_teams(
        self,
        repositories: RepositoryFactory,
        items: list[dict[str, Any]],
        department_map: dict[str, Any],
    ) -> dict[str, Any]:
        prepared_items = []
        for item in items:
            prepared_items.append({
                **item,
                "department_id": department_map[item["department_code"]],
            })
        return await self._seed_entities(repositories, Team, prepared_items, key_field="code")

    async def _seed_permissions(
        self,
        repositories: RepositoryFactory,
        items: list[dict[str, Any]],
    ) -> dict[str, Any]:
        return await self._seed_entities(repositories, Permission, items, key_field="code")

    async def _seed_roles(
        self,
        repositories: RepositoryFactory,
        items: list[dict[str, Any]],
        organization_map: dict[str, Any],
    ) -> dict[str, Any]:
        prepared_items = []
        for item in items:
            organization_code = item.get("organization_code")
            prepared_items.append(
                {
                    **item,
                    "organization_id": organization_map.get(organization_code) if organization_code else None,
                }
            )
        return await self._seed_entities(repositories, Role, prepared_items, key_field="code")

    async def _seed_settings(self, repositories: RepositoryFactory, items: list[dict[str, Any]]) -> dict[str, Any]:
        return await self._seed_entities(repositories, SystemSetting, items, key_field="setting_key")

    async def _seed_feature_flags(self, repositories: RepositoryFactory, items: list[dict[str, Any]]) -> dict[str, Any]:
        return await self._seed_entities(repositories, FeatureFlag, items, key_field="flag_key")

    async def _seed_role_permissions(
        self,
        session: AsyncSession,
        items: list[dict[str, Any]],
        role_map: dict[str, Any],
        permission_map: dict[str, Any],
    ) -> int:
        repository = RepositoryFactory(session).create(RolePermission)
        inserted = 0
        for item in items:
            role_id = role_map[item["role_code"]]
            permission_id = permission_map[item["permission_code"]]
            if not await repository.exists({"role_id": role_id, "permission_id": permission_id}):
                await repository.create(RolePermission(role_id=role_id, permission_id=permission_id))
                inserted += 1
        return inserted

    async def _seed_entities(
        self,
        repositories: RepositoryFactory,
        model: type[Any],
        items: list[dict[str, Any]],
        *,
        key_field: str,
    ) -> dict[str, Any]:
        repository = repositories.create(model)
        inserted: dict[str, Any] = {}
        for item in items:
            key_value = item[key_field]
            if not await repository.exists({key_field: key_value}):
                model_payload = {key: value for key, value in item.items() if hasattr(model, key)}
                entity = model(**model_payload)
                if hasattr(entity, "id") and getattr(entity, "id", None) is None:
                    setattr(entity, "id", uuid4())
                entity = await repository.create(entity)
                inserted[key_value] = entity.id
        return inserted
