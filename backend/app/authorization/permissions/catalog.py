from __future__ import annotations

DEFAULT_PERMISSION_CODES: list[str] = [
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

DEFAULT_ROLE_DEFINITIONS: list[dict[str, object]] = [
    {"code": "super_admin", "name": "Super Admin", "permissions": DEFAULT_PERMISSION_CODES},
    {"code": "security_admin", "name": "Security Admin", "permissions": ["User.Read", "User.Write", "Role.Read", "Role.Write", "Audit.Read", "Audit.Export", "Settings.Read", "Settings.Write", "System.Admin"]},
    {"code": "soc_manager", "name": "SOC Manager", "permissions": ["Dashboard.Read", "Threat.Read", "Threat.Write", "Audit.Read", "Report.Read", "Report.Export"]},
    {"code": "soc_analyst", "name": "SOC Analyst", "permissions": ["Dashboard.Read", "Threat.Read", "Audit.Read", "Report.Read"]},
    {"code": "fraud_analyst", "name": "Fraud Analyst", "permissions": ["Fraud.Read", "Fraud.Write", "Audit.Read", "Report.Read"]},
    {"code": "security_engineer", "name": "Security Engineer", "permissions": ["Threat.Read", "Threat.Write", "Settings.Read", "Settings.Write"]},
    {"code": "compliance_officer", "name": "Compliance Officer", "permissions": ["Audit.Read", "Audit.Export", "Report.Read", "Report.Export"]},
    {"code": "executive", "name": "Executive", "permissions": ["Dashboard.Read", "Report.Read", "Report.Export"]},
    {"code": "auditor", "name": "Auditor", "permissions": ["Audit.Read", "Audit.Export", "Report.Read", "Report.Export"]},
    {"code": "read_only", "name": "Read Only", "permissions": ["User.Read", "Role.Read", "Audit.Read", "Dashboard.Read", "Threat.Read", "Fraud.Read", "Report.Read", "AI.Read", "Settings.Read"]},
]

DEFAULT_ROLE_HIERARCHY: list[tuple[str, str]] = [
    ("super_admin", "security_admin"),
    ("security_admin", "soc_manager"),
    ("soc_manager", "soc_analyst"),
    ("soc_analyst", "read_only"),
]

DEFAULT_PERMISSION_GROUPS: list[dict[str, object]] = [
    {"code": "identity_admin", "name": "Identity Administration", "permissions": ["User.Read", "User.Write", "User.Delete", "Role.Read", "Role.Write", "Role.Delete"]},
    {"code": "security_operations", "name": "Security Operations", "permissions": ["Audit.Read", "Audit.Export", "Dashboard.Read", "Threat.Read", "Threat.Write"]},
    {"code": "fraud_operations", "name": "Fraud Operations", "permissions": ["Fraud.Read", "Fraud.Write"]},
    {"code": "reporting", "name": "Reporting", "permissions": ["Report.Read", "Report.Export"]},
    {"code": "platform_admin", "name": "Platform Administration", "permissions": ["AI.Read", "AI.Execute", "Settings.Read", "Settings.Write", "System.Admin"]},
]
