"""enterprise rbac authorization

Revision ID: 0003_enterprise_rbac_authorization
Revises: 0002_auth_identity_management
Create Date: 2026-07-14 00:00:00.000002
"""

from __future__ import annotations

from uuid import NAMESPACE_URL, uuid5

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects.postgresql import insert


revision = "0003_enterprise_rbac_authorization"
down_revision = "0002_auth_identity_management"
branch_labels = None
depends_on = None


def _uuid(kind: str, code: str):
    return uuid5(NAMESPACE_URL, f"sentinel:{kind}:{code}")


def upgrade() -> None:
    op.create_table(
        "permission_groups",
        sa.Column("id", sa.Uuid(as_uuid=True), primary_key=True, nullable=False),
        sa.Column("code", sa.String(length=128), nullable=False),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("status", sa.String(length=32), nullable=False, server_default="active"),
        sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("created_by", sa.String(length=255), nullable=True),
        sa.Column("updated_by", sa.String(length=255), nullable=True),
        sa.Column("created_source", sa.String(length=255), nullable=True),
        sa.Column("updated_source", sa.String(length=255), nullable=True),
        sa.Column("correlation_id", sa.String(length=64), nullable=True),
        sa.Column("version", sa.Integer(), nullable=False, server_default="1"),
        sa.UniqueConstraint("code", name="uq_permission_groups_code"),
    )
    op.create_index("ix_permission_groups_status", "permission_groups", ["status"], unique=False)

    op.create_table(
        "permission_group_permissions",
        sa.Column("group_id", sa.Uuid(as_uuid=True), sa.ForeignKey("permission_groups.id", ondelete="CASCADE"), primary_key=True),
        sa.Column("permission_id", sa.Uuid(as_uuid=True), sa.ForeignKey("permissions.id", ondelete="CASCADE"), primary_key=True),
        sa.Column("granted_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("created_by", sa.String(length=255), nullable=True),
        sa.Column("updated_by", sa.String(length=255), nullable=True),
        sa.Column("created_source", sa.String(length=255), nullable=True),
        sa.Column("updated_source", sa.String(length=255), nullable=True),
        sa.Column("correlation_id", sa.String(length=64), nullable=True),
        sa.UniqueConstraint("group_id", "permission_id", name="uq_permission_group_permissions_group_permission"),
    )
    op.create_index("ix_permission_group_permissions_group_id", "permission_group_permissions", ["group_id"], unique=False)
    op.create_index("ix_permission_group_permissions_permission_id", "permission_group_permissions", ["permission_id"], unique=False)

    op.create_table(
        "role_hierarchy",
        sa.Column("parent_role_id", sa.Uuid(as_uuid=True), sa.ForeignKey("roles.id", ondelete="CASCADE"), primary_key=True),
        sa.Column("child_role_id", sa.Uuid(as_uuid=True), sa.ForeignKey("roles.id", ondelete="CASCADE"), primary_key=True),
        sa.Column("depth", sa.Integer(), nullable=False, server_default="1"),
        sa.Column("active", sa.Boolean(), nullable=False, server_default=sa.text("true")),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("created_by", sa.String(length=255), nullable=True),
        sa.Column("updated_by", sa.String(length=255), nullable=True),
        sa.Column("created_source", sa.String(length=255), nullable=True),
        sa.Column("updated_source", sa.String(length=255), nullable=True),
        sa.Column("correlation_id", sa.String(length=64), nullable=True),
        sa.UniqueConstraint("parent_role_id", "child_role_id", name="uq_role_hierarchy_parent_child"),
    )
    op.create_index("ix_role_hierarchy_parent_role_id", "role_hierarchy", ["parent_role_id"], unique=False)
    op.create_index("ix_role_hierarchy_child_role_id", "role_hierarchy", ["child_role_id"], unique=False)

    op.create_table(
        "authorization_policies",
        sa.Column("id", sa.Uuid(as_uuid=True), primary_key=True, nullable=False),
        sa.Column("code", sa.String(length=128), nullable=False),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("effect", sa.String(length=16), nullable=False, server_default="allow"),
        sa.Column("priority", sa.Integer(), nullable=False, server_default="100"),
        sa.Column("subject_type", sa.String(length=32), nullable=False, server_default="role"),
        sa.Column("subject_value", sa.String(length=128), nullable=True),
        sa.Column("resource", sa.String(length=128), nullable=False),
        sa.Column("action", sa.String(length=64), nullable=False),
        sa.Column("conditions", sa.JSON(), nullable=False, server_default=sa.text("'{}'::json")),
        sa.Column("enabled", sa.Boolean(), nullable=False, server_default=sa.text("true")),
        sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("created_by", sa.String(length=255), nullable=True),
        sa.Column("updated_by", sa.String(length=255), nullable=True),
        sa.Column("created_source", sa.String(length=255), nullable=True),
        sa.Column("updated_source", sa.String(length=255), nullable=True),
        sa.Column("correlation_id", sa.String(length=64), nullable=True),
        sa.Column("version", sa.Integer(), nullable=False, server_default="1"),
        sa.UniqueConstraint("code", name="uq_authorization_policies_code"),
    )
    op.create_index("ix_authorization_policies_priority", "authorization_policies", ["priority"], unique=False)
    op.create_index("ix_authorization_policies_resource_action", "authorization_policies", ["resource", "action"], unique=False)
    op.create_index("ix_authorization_policies_effect_enabled", "authorization_policies", ["effect", "enabled"], unique=False)

    connection = op.get_bind()

    permission_rows = []
    permission_codes = [
        "User.Read",
        "User.Write",
        "User.Delete",
        "Role.Read",
        "Role.Write",
        "Role.Delete",
        "Audit.Read",
        "Audit.Export",
        "Dashboard.Read",
        "Threat.Read",
        "Threat.Write",
        "Fraud.Read",
        "Fraud.Write",
        "Report.Read",
        "Report.Export",
        "AI.Read",
        "AI.Execute",
        "Settings.Read",
        "Settings.Write",
        "System.Admin",
    ]
    for code in permission_codes:
        resource, action = code.split(".", 1) if "." in code else (code.lower(), code.lower())
        permission_rows.append({"id": _uuid("permission", code), "code": code, "resource": resource, "action": action, "description": f"Default permission for {code}", "category": resource.lower(), "created_at": sa.func.now(), "updated_at": sa.func.now(), "status": "active"})
    permission_insert = insert(sa.table("permissions", sa.column("id"), sa.column("code"), sa.column("resource"), sa.column("action"), sa.column("description"), sa.column("category"), sa.column("created_at"), sa.column("updated_at"))).values(permission_rows)
    connection.execute(permission_insert.on_conflict_do_nothing(index_elements=["code"]))

    role_rows = []
    role_definitions = [
        ("super_admin", "Super Admin"),
        ("security_admin", "Security Admin"),
        ("soc_manager", "SOC Manager"),
        ("soc_analyst", "SOC Analyst"),
        ("fraud_analyst", "Fraud Analyst"),
        ("security_engineer", "Security Engineer"),
        ("compliance_officer", "Compliance Officer"),
        ("executive", "Executive"),
        ("auditor", "Auditor"),
        ("read_only", "Read Only"),
    ]
    for code, name in role_definitions:
        role_rows.append({"id": _uuid("role", code), "code": code, "name": name, "description": f"Default role {name}", "status": "active", "created_at": sa.func.now(), "updated_at": sa.func.now()})
    role_insert = insert(sa.table("roles", sa.column("id"), sa.column("code"), sa.column("name"), sa.column("description"), sa.column("status"), sa.column("created_at"), sa.column("updated_at"))).values(role_rows)
    connection.execute(role_insert.on_conflict_do_nothing(index_elements=["code"]))

    role_permission_rows = []
    role_permission_map = {
        "super_admin": permission_codes,
        "security_admin": ["User.Read", "User.Write", "Role.Read", "Role.Write", "Audit.Read", "Audit.Export", "Settings.Read", "Settings.Write", "System.Admin"],
        "soc_manager": ["Dashboard.Read", "Threat.Read", "Threat.Write", "Audit.Read", "Report.Read", "Report.Export"],
        "soc_analyst": ["Dashboard.Read", "Threat.Read", "Audit.Read", "Report.Read"],
        "fraud_analyst": ["Fraud.Read", "Fraud.Write", "Audit.Read", "Report.Read"],
        "security_engineer": ["Threat.Read", "Threat.Write", "Settings.Read", "Settings.Write"],
        "compliance_officer": ["Audit.Read", "Audit.Export", "Report.Read", "Report.Export"],
        "executive": ["Dashboard.Read", "Report.Read", "Report.Export"],
        "auditor": ["Audit.Read", "Audit.Export", "Report.Read", "Report.Export"],
        "read_only": ["User.Read", "Role.Read", "Audit.Read", "Dashboard.Read", "Threat.Read", "Fraud.Read", "Report.Read", "AI.Read", "Settings.Read"],
    }
    for role_code, assigned_permissions in role_permission_map.items():
        for permission_code in assigned_permissions:
            role_permission_rows.append({"role_id": _uuid("role", role_code), "permission_id": _uuid("permission", permission_code), "granted_at": sa.func.now()})
    role_permission_insert = insert(sa.table("role_permissions", sa.column("role_id"), sa.column("permission_id"), sa.column("granted_at"))).values(role_permission_rows)
    connection.execute(role_permission_insert.on_conflict_do_nothing(index_elements=["role_id", "permission_id"]))

    hierarchy_rows = [
        {"parent_role_id": _uuid("role", "super_admin"), "child_role_id": _uuid("role", "security_admin"), "depth": 1, "active": True, "created_at": sa.func.now()},
        {"parent_role_id": _uuid("role", "security_admin"), "child_role_id": _uuid("role", "soc_manager"), "depth": 1, "active": True, "created_at": sa.func.now()},
        {"parent_role_id": _uuid("role", "soc_manager"), "child_role_id": _uuid("role", "soc_analyst"), "depth": 1, "active": True, "created_at": sa.func.now()},
        {"parent_role_id": _uuid("role", "soc_analyst"), "child_role_id": _uuid("role", "read_only"), "depth": 1, "active": True, "created_at": sa.func.now()},
    ]
    hierarchy_insert = insert(sa.table("role_hierarchy", sa.column("parent_role_id"), sa.column("child_role_id"), sa.column("depth"), sa.column("active"), sa.column("created_at"))).values(hierarchy_rows)
    connection.execute(hierarchy_insert.on_conflict_do_nothing(index_elements=["parent_role_id", "child_role_id"]))

    group_rows = []
    permission_groups = [
        ("identity_admin", "Identity Administration"),
        ("security_operations", "Security Operations"),
        ("fraud_operations", "Fraud Operations"),
        ("reporting", "Reporting"),
        ("platform_admin", "Platform Administration"),
    ]
    for code, name in permission_groups:
        group_rows.append({"id": _uuid("group", code), "code": code, "name": name, "description": f"Default permission group {name}", "status": "active", "created_at": sa.func.now(), "updated_at": sa.func.now()})
    group_insert = insert(sa.table("permission_groups", sa.column("id"), sa.column("code"), sa.column("name"), sa.column("description"), sa.column("status"), sa.column("created_at"), sa.column("updated_at"))).values(group_rows)
    connection.execute(group_insert.on_conflict_do_nothing(index_elements=["code"]))

    group_permission_rows = []
    group_map = {
        "identity_admin": ["User.Read", "User.Write", "User.Delete", "Role.Read", "Role.Write", "Role.Delete"],
        "security_operations": ["Audit.Read", "Audit.Export", "Dashboard.Read", "Threat.Read", "Threat.Write"],
        "fraud_operations": ["Fraud.Read", "Fraud.Write"],
        "reporting": ["Report.Read", "Report.Export"],
        "platform_admin": ["AI.Read", "AI.Execute", "Settings.Read", "Settings.Write", "System.Admin"],
    }
    for group_code, assigned_permissions in group_map.items():
        for permission_code in assigned_permissions:
            group_permission_rows.append({"group_id": _uuid("group", group_code), "permission_id": _uuid("permission", permission_code), "granted_at": sa.func.now()})
    group_permission_insert = insert(sa.table("permission_group_permissions", sa.column("group_id"), sa.column("permission_id"), sa.column("granted_at"))).values(group_permission_rows)
    connection.execute(group_permission_insert.on_conflict_do_nothing(index_elements=["group_id", "permission_id"]))


def downgrade() -> None:
    op.drop_table("authorization_policies")
    op.drop_index("ix_role_hierarchy_child_role_id", table_name="role_hierarchy")
    op.drop_index("ix_role_hierarchy_parent_role_id", table_name="role_hierarchy")
    op.drop_table("role_hierarchy")
    op.drop_index("ix_permission_group_permissions_permission_id", table_name="permission_group_permissions")
    op.drop_index("ix_permission_group_permissions_group_id", table_name="permission_group_permissions")
    op.drop_table("permission_group_permissions")
    op.drop_index("ix_permission_groups_status", table_name="permission_groups")
    op.drop_table("permission_groups")
