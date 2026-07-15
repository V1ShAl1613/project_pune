"use client";

// Shared IAM page shell used across identity, RBAC, and administration views.
import Link from "next/link";
import type { Route } from "next";

import { ArrowRight, ShieldCheck } from "lucide-react";

import { Button } from "@/components/ui/controls";
import { Badge, Card } from "@/components/ui/surfaces";
import { DashboardShell } from "@/dashboard/layouts/dashboard-shell";
import { cn } from "@/lib/cn";

type IdentityPageShellProps = {
  eyebrow: string;
  title: string;
  description: string;
  status?: string;
  actions?: Array<{ label: string; href: string; variant?: "primary" | "secondary" | "ghost" }>;
  children: React.ReactNode;
  stats?: Array<{ label: string; value: string; detail: string }>;
  className?: string;
};

export function IdentityPageShell({ eyebrow, title, description, status = "enterprise", actions = [], children, stats = [], className }: IdentityPageShellProps): React.JSX.Element {
  return (
    <DashboardShell className={className}>
      <div className="space-y-6 py-6">
        <Card className="overflow-hidden border-line/80 bg-panel/90 shadow-soft">
          <div className="grid gap-6 p-6 lg:grid-cols-[1.2fr_0.8fr] lg:p-8">
            <div className="space-y-4">
              <Badge tone="neutral">{eyebrow}</Badge>
              <div className="space-y-2">
                <div className="inline-flex items-center gap-2 rounded-full border border-line bg-canvas px-3 py-1 text-xs font-medium uppercase tracking-[0.2em] text-muted">
                  <ShieldCheck className="h-3.5 w-3.5" />
                  {status}
                </div>
                <h1 className="max-w-3xl text-3xl font-semibold tracking-tight text-text sm:text-4xl">{title}</h1>
                <p className="max-w-3xl text-sm leading-6 text-muted sm:text-base">{description}</p>
              </div>
              {actions.length > 0 ? (
                <div className="flex flex-wrap gap-3">
                  {actions.map((action) => (
                    <Link key={action.href} href={action.href as Route}>
                      <Button variant={action.variant ?? "primary"}>
                        {action.label}
                        <ArrowRight className="h-4 w-4" />
                      </Button>
                    </Link>
                  ))}
                </div>
              ) : null}
            </div>
            <div className="grid gap-3 sm:grid-cols-2 lg:grid-cols-2">
              {stats.map((stat) => (
                <div key={stat.label} className="rounded-2xl border border-line bg-canvas p-4">
                  <div className="text-xs uppercase tracking-wide text-muted">{stat.label}</div>
                  <div className="mt-2 text-2xl font-semibold text-text">{stat.value}</div>
                  <div className="mt-1 text-sm text-muted">{stat.detail}</div>
                </div>
              ))}
            </div>
          </div>
        </Card>

        <div className={cn("space-y-6", className)}>{children}</div>
      </div>
    </DashboardShell>
  );
}