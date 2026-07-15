"use client";

// Small visual panels used by the SOC dashboard and investigation views.
import type { ReactNode } from "react";

import { Card } from "@/components/ui/surfaces";

export function StatPanel({ title, value, detail }: { title: string; value: string; detail: string }): React.JSX.Element {
  return <Card className="space-y-2"><div className="text-xs uppercase tracking-wide text-muted">{title}</div><div className="text-3xl font-semibold text-text">{value}</div><div className="text-sm text-muted">{detail}</div></Card>;
}

export function SectionPanel({ title, description, children }: { title: string; description?: string; children: ReactNode }): React.JSX.Element {
  return <Card className="space-y-4"><div><h3 className="text-base font-semibold text-text">{title}</h3>{description ? <p className="text-sm text-muted">{description}</p> : null}</div>{children}</Card>;
}

export function Grid({ children }: { children: ReactNode }): React.JSX.Element {
  return <div className="grid gap-4 lg:grid-cols-2 xl:grid-cols-4">{children}</div>;
}
