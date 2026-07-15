// Dashboard framework model definitions and shared static structures.
export type DashboardSectionKey =
  | "dashboard"
  | "soc-center"
  | "alerts"
  | "cases"
  | "timeline"
  | "iocs"
  | "threats"
  | "intel"
  | "attack"
  | "workbench"
  | "mitre"
  | "tenants"
  | "workspaces"
  | "threat-center"
  | "soc-center"
  | "fraud-center"
  | "risk-center"
  | "compliance-center"
  | "roles"
  | "permissions"
  | "groups"
  | "invitations"
  | "sessions"
  | "apikeys"
  | "service-accounts"
  | "sso"
  | "mfa"
  | "audit"
  | "users"
  | "organizations"
  | "assets"
  | "incidents"
  | "investigations"
  | "reports"
  | "administration"
  | "settings"
  | "audit-logs"
  | "integrations";

export type DashboardNavigationItem = {
  key: DashboardSectionKey;
  label: string;
  href: string;
  icon: string;
  description: string;
  pinned?: boolean;
  recent?: boolean;
  favorite?: boolean;
};

export type DashboardWidgetSize = "sm" | "md" | "lg" | "xl";

export type DashboardWidget = {
  id: string;
  title: string;
  description: string;
  size: DashboardWidgetSize;
  pinned?: boolean;
  favorite?: boolean;
};

export const dashboardNavigation: DashboardNavigationItem[] = [
  { key: "dashboard", label: "Dashboard", href: "/dashboard", icon: "layout-dashboard", description: "Workspace overview", pinned: true, recent: true, favorite: true },
  { key: "soc-center", label: "SOC Center", href: "/soc-center", icon: "radar", description: "Security operations overview", pinned: true, recent: true },
  { key: "alerts", label: "Alerts", href: "/alerts", icon: "siren", description: "Alert triage and queue" },
  { key: "cases", label: "Cases", href: "/cases", icon: "clipboard-list", description: "Structured investigations" },
  { key: "timeline", label: "Timeline", href: "/timeline", icon: "git-branch", description: "Chronology and activity" },
  { key: "iocs", label: "IOCs", href: "/iocs", icon: "target", description: "Indicator tracking" },
  { key: "threats", label: "Threats", href: "/threat-center", icon: "shield-alert", description: "Threat intelligence feed" },
  { key: "intel", label: "Intel", href: "/intel", icon: "globe", description: "Threat actors and campaigns" },
  { key: "attack", label: "Attack", href: "/attack", icon: "workflow", description: "React Flow attack graph" },
  { key: "workbench", label: "Workbench", href: "/workbench", icon: "square-terminal", description: "Analyst workspace" },
  { key: "mitre", label: "MITRE", href: "/mitre", icon: "map", description: "ATT&CK matrix and coverage" },
  { key: "tenants", label: "Tenants", href: "/tenants", icon: "shield-check", description: "Tenant isolation and health" },
  { key: "workspaces", label: "Workspaces", href: "/workspaces", icon: "building-2", description: "Workspace switching and context" },
  { key: "threat-center", label: "Threat Center", href: "/threat-center", icon: "shield-alert", description: "UI shell only" },
  { key: "soc-center", label: "SOC Center", href: "/soc-center", icon: "radar", description: "UI shell only" },
  { key: "fraud-center", label: "Fraud Center", href: "/fraud-center", icon: "banknote", description: "UI shell only" },
  { key: "risk-center", label: "Risk Center", href: "/risk-center", icon: "gauge", description: "UI shell only" },
  { key: "compliance-center", label: "Compliance Center", href: "/compliance-center", icon: "shield-check", description: "UI shell only" },
  { key: "roles", label: "Roles", href: "/roles", icon: "shield-check", description: "Role lifecycle and matrix" },
  { key: "permissions", label: "Permissions", href: "/permissions", icon: "sliders-horizontal", description: "Permission tree and preview" },
  { key: "groups", label: "Groups", href: "/groups", icon: "users", description: "Nested and dynamic groups" },
  { key: "invitations", label: "Invitations", href: "/invitations", icon: "scroll-text", description: "Bulk invite workflows" },
  { key: "sessions", label: "Sessions", href: "/sessions", icon: "clock", description: "Active session controls" },
  { key: "apikeys", label: "API Keys", href: "/apikeys", icon: "file-text", description: "Key rotation and scopes" },
  { key: "service-accounts", label: "Service Accounts", href: "/service-accounts", icon: "server", description: "Automations and secrets" },
  { key: "sso", label: "SSO", href: "/sso", icon: "plug", description: "Enterprise identity providers" },
  { key: "mfa", label: "MFA", href: "/mfa", icon: "shield-alert", description: "Passkeys and recovery" },
  { key: "audit", label: "Audit", href: "/audit", icon: "scroll-text", description: "Audit timeline and export" },
  { key: "users", label: "Users", href: "/users", icon: "users", description: "Identity module" },
  { key: "organizations", label: "Organizations", href: "/organizations", icon: "building-2", description: "Identity module" },
  { key: "assets", label: "Assets", href: "/assets", icon: "server", description: "UI shell only" },
  { key: "incidents", label: "Incidents", href: "/incidents", icon: "triangle-alert", description: "UI shell only" },
  { key: "investigations", label: "Investigations", href: "/investigations", icon: "folder-search", description: "UI shell only" },
  { key: "reports", label: "Reports", href: "/reports", icon: "file-text", description: "UI shell only" },
  { key: "administration", label: "Administration", href: "/administration", icon: "settings-2", description: "UI shell only" },
  { key: "settings", label: "Settings", href: "/settings", icon: "sliders-horizontal", description: "Preferences and appearance" },
  { key: "audit-logs", label: "Audit Logs", href: "/audit-logs", icon: "scroll-text", description: "UI shell only" },
  { key: "integrations", label: "Integrations", href: "/integrations", icon: "plug", description: "UI shell only" },
];

export const dashboardWidgets: DashboardWidget[] = [
  { id: "kpi-1", title: "Enterprise KPI", description: "Quick summary tile", size: "sm", pinned: true, favorite: true },
  { id: "kpi-2", title: "Trend Overview", description: "Trend-ready summary", size: "md", pinned: true },
  { id: "kpi-3", title: "Status Meter", description: "Operational health", size: "sm", favorite: true },
  { id: "kpi-4", title: "Workflow Panel", description: "Dynamic panel container", size: "lg" },
];
