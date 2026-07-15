"use client";

// Shared list-page wrapper for alerts, incidents, cases, IOC, threat, and asset views.
import type { ColumnDef } from "@tanstack/react-table";

import { SocShell } from "@/soc/shared/soc-shell";
import { SocTable } from "@/soc/shared/soc-table";
import { Card } from "@/components/ui/surfaces";

type SocListPageProps<TData> = {
  eyebrow: string;
  title: string;
  description: string;
  status?: string;
  stats: Array<{ label: string; value: string; detail: string }>;
  data: TData[];
  columns: ColumnDef<TData, any>[];
  searchPlaceholder?: string;
  actions?: Array<{ label: string; href: string; variant?: "primary" | "secondary" | "ghost" }>;
  topPanel?: React.ReactNode;
};

export function SocListPage<TData>({ eyebrow, title, description, status, stats, data, columns, searchPlaceholder, actions, topPanel }: SocListPageProps<TData>): React.JSX.Element {
  return (
    <SocShell eyebrow={eyebrow} title={title} description={description} status={status} actions={actions} stats={stats}>
      {topPanel ? <Card className="space-y-4">{topPanel}</Card> : null}
      <SocTable title={title} description={description} data={data} columns={columns} searchPlaceholder={searchPlaceholder} />
    </SocShell>
  );
}
