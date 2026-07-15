"use client";

// Shared page renderer for list-driven IAM screens with a consistent enterprise layout.
import { type ColumnDef } from "@tanstack/react-table";

import { IdentityPageShell } from "@/identity/shared/iam-page-shell";
import { IdentityTable } from "@/identity/shared/iam-table";
import { SectionCard, SectionGrid, EmptyState } from "@/identity/shared/iam-section";
import { Badge } from "@/components/ui/surfaces";

type IdentityListPageProps<TData> = {
  eyebrow: string;
  title: string;
  description: string;
  status?: string;
  stats: Array<{ label: string; value: string; detail: string }>;
  actions?: Array<{ label: string; href: string; variant?: "primary" | "secondary" | "ghost" }>;
  columns: ColumnDef<TData, any>[];
  data: TData[];
  searchPlaceholder?: string;
  topSummary?: React.ReactNode;
  secondaryPanels?: React.ReactNode;
};

export function IdentityListPage<TData>({ eyebrow, title, description, status, stats, actions, columns, data, searchPlaceholder, topSummary, secondaryPanels }: IdentityListPageProps<TData>): React.JSX.Element {
  return (
    <IdentityPageShell eyebrow={eyebrow} title={title} description={description} status={status} actions={actions} stats={stats}>
      <SectionGrid>
        <SectionCard title="Summary" description="Static UI demo data for enterprise IAM composition.">
          <div className="flex flex-wrap gap-2">{stats.map((stat) => <Badge key={stat.label} tone="neutral">{stat.label}: {stat.value}</Badge>)}</div>
          {topSummary ?? <EmptyState title="Ready for backend wiring" description="This screen is frontend-only and designed for API-backed data hydration." />}
        </SectionCard>
        <SectionCard title="Controls" description="Sorting, search, pagination, and bulk-action rails are built in.">
          <div className="space-y-2 text-sm text-muted">
            <div>Table controls: search, refresh, export, selection, and paging.</div>
            <div>Forms and mutation dialogs can be layered on top of this shell.</div>
          </div>
        </SectionCard>
      </SectionGrid>

      {secondaryPanels}

      <IdentityTable title={title} description={description} data={data} columns={columns} searchPlaceholder={searchPlaceholder} />
    </IdentityPageShell>
  );
}