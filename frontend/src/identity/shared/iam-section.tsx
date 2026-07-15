"use client";

// Small reusable card and banner helpers used across IAM screens.
import type { ReactNode } from "react";

import { Card } from "@/components/ui/surfaces";
import { cn } from "@/lib/cn";

export function SectionGrid({ children, className }: { children: ReactNode; className?: string }): React.JSX.Element {
  return <div className={cn("grid gap-4 lg:grid-cols-2", className)}>{children}</div>;
}

export function SectionCard({ title, description, children, className }: { title: string; description?: string; children: ReactNode; className?: string }): React.JSX.Element {
  return <Card className={cn("space-y-4", className)}><div><h3 className="text-base font-semibold text-text">{title}</h3>{description ? <p className="text-sm text-muted">{description}</p> : null}</div>{children}</Card>;
}

export function EmptyState({ title, description }: { title: string; description: string }): React.JSX.Element {
  return <div className="rounded-3xl border border-dashed border-line bg-canvas p-6 text-sm text-muted"><div className="text-base font-semibold text-text">{title}</div><p className="mt-1">{description}</p></div>;
}