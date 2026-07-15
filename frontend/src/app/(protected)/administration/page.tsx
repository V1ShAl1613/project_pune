"use client";

import { createColumnHelper } from "@tanstack/react-table";
import { Activity, BadgeCheck, KeyRound, ShieldAlert, Users2 } from "lucide-react";

import { IdentityTable } from "@/identity/shared/iam-table";
import { IdentityPageShell } from "@/identity/shared/iam-page-shell";
import { demoApiKeys, demoAuditEvents, demoOrganizations, demoRoles, demoSessions, demoTenants, demoUsers } from "@/identity/shared/iam-demo-data";
import { SectionCard, SectionGrid } from "@/identity/shared/iam-section";
import { Badge } from "@/components/ui/surfaces";
import { Button } from "@/components/ui/controls";
import type { AuditEvent, Role } from "@/types/identity";

const roleColumnHelper = createColumnHelper<Role>();
const auditColumnHelper = createColumnHelper<AuditEvent>();

const roleColumns = [
  roleColumnHelper.accessor("name", { header: "Role", cell: (info) => <div className="font-medium text-text">{info.getValue()}</div> }),
  roleColumnHelper.accessor("key", { header: "Key" }),
  roleColumnHelper.accessor("status", { header: "Status", cell: (info) => <Badge tone={info.getValue() === "active" ? "success" : "neutral"}>{info.getValue()}</Badge> }),
];

const auditColumns = [
  auditColumnHelper.accessor("timestamp", { header: "Timestamp", cell: (info) => <div className="text-sm text-muted">{info.getValue()}</div> }),
  auditColumnHelper.accessor("actor", { header: "Actor" }),
  auditColumnHelper.accessor("action", { header: "Action" }),
  auditColumnHelper.accessor("severity", { header: "Severity", cell: (info) => <Badge tone={info.getValue() === "critical" || info.getValue() === "high" ? "danger" : info.getValue() === "medium" ? "warning" : "neutral"}>{info.getValue()}</Badge> }),
];

export default function AdministrationPage(): React.JSX.Element {
  return (
    <IdentityPageShell
      eyebrow="Enterprise administration"
      title="Administration dashboard"
      description="System health placeholder, users summary, organizations summary, workspaces summary, roles summary, sessions summary, API keys summary, quick actions, and recent changes."
      status="iam operations"
      actions={[
        { label: "Open roles", href: "/roles" },
        { label: "Open audit", href: "/audit", variant: "secondary" },
      ]}
      stats={[
        { label: "Tenants", value: String(demoTenants.length), detail: "Tenant inventory" },
        { label: "Users", value: String(demoUsers.length), detail: "User directory snapshot" },
        { label: "Organizations", value: String(demoOrganizations.length), detail: "Scoped orgs" },
        { label: "API Keys", value: String(demoApiKeys.length), detail: "Key lifecycle" },
      ]}
    >
      <SectionGrid className="lg:grid-cols-2">
        <SectionCard title="System health" description="Frontend placeholder for service health, auth health, and tenant readiness.">
          <div className="grid gap-3 sm:grid-cols-2">
            <div className="rounded-2xl border border-line bg-canvas p-4">
              <div className="flex items-center gap-2 text-sm font-semibold text-text"><BadgeCheck className="h-4 w-4 text-success" />Authentication</div>
              <div className="mt-1 text-sm text-muted">Session UI healthy</div>
            </div>
            <div className="rounded-2xl border border-line bg-canvas p-4">
              <div className="flex items-center gap-2 text-sm font-semibold text-text"><ShieldAlert className="h-4 w-4 text-warning" />Tenant limits</div>
              <div className="mt-1 text-sm text-muted">Limit cards ready</div>
            </div>
            <div className="rounded-2xl border border-line bg-canvas p-4">
              <div className="flex items-center gap-2 text-sm font-semibold text-text"><Users2 className="h-4 w-4 text-accent" />Identity directory</div>
              <div className="mt-1 text-sm text-muted">Users, roles, groups</div>
            </div>
            <div className="rounded-2xl border border-line bg-canvas p-4">
              <div className="flex items-center gap-2 text-sm font-semibold text-text"><KeyRound className="h-4 w-4 text-primary" />Secrets</div>
              <div className="mt-1 text-sm text-muted">API keys and accounts</div>
            </div>
          </div>
        </SectionCard>

        <SectionCard title="Quick actions" description="Administration entry points for operators and tenant admins.">
          <div className="flex flex-wrap gap-3">
            <Button>Invite user</Button>
            <Button variant="secondary">Create role</Button>
            <Button variant="secondary">Rotate API key</Button>
            <Button variant="secondary">Export audit</Button>
          </div>
          <div className="grid gap-3 pt-4 sm:grid-cols-2">
            <div className="rounded-2xl border border-line bg-canvas p-4">
              <div className="text-sm font-semibold text-text">Recent changes</div>
              <div className="mt-2 text-sm text-muted">Role assignment, session updates, and organization changes are surfaced here.</div>
            </div>
            <div className="rounded-2xl border border-line bg-canvas p-4">
              <div className="text-sm font-semibold text-text">Statistics cards</div>
              <div className="mt-2 text-sm text-muted">Users, roles, sessions, API keys, and organizations summary tiles are pre-wired.</div>
            </div>
          </div>
        </SectionCard>
      </SectionGrid>

      <SectionGrid className="lg:grid-cols-2">
        <SectionCard title="RBAC review" description="Role list snapshot and recent change feed used in the administration hub.">
          <IdentityTable title="Roles snapshot" description="Role list and quick review table." data={demoRoles} columns={roleColumns} searchPlaceholder="Search roles" density="compact" />
        </SectionCard>

        <SectionCard title="Recent audit events" description="Timeline, filters, and export behavior are ready for backend hookup.">
          <IdentityTable title="Audit events" description="Identity and RBAC events." data={demoAuditEvents} columns={auditColumns} searchPlaceholder="Search audit events" density="compact" />
        </SectionCard>
      </SectionGrid>
    </IdentityPageShell>
  );
}
