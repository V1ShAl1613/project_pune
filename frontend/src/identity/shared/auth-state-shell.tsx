// Shared shell for public authentication and account-state screens.
import Link from "next/link";
import type { Route } from "next";

import { ArrowRight, ShieldAlert } from "lucide-react";

import { Button } from "@/components/ui/controls";
import { Card } from "@/components/ui/surfaces";

type AuthStateShellProps = {
  title: string;
  description: string;
  accent?: string;
  actions?: Array<{ label: string; href: string; variant?: "primary" | "secondary" | "ghost" }>;
  children?: React.ReactNode;
};

export function AuthStateShell({ title, description, accent = "Enterprise access state", actions = [], children }: AuthStateShellProps): React.JSX.Element {
  return <div className="grid w-full gap-6 lg:grid-cols-[1fr_auto]"><div className="max-w-xl space-y-4"><div className="inline-flex items-center gap-2 rounded-full border border-line bg-panel px-3 py-1 text-xs font-medium uppercase tracking-[0.2em] text-muted"><ShieldAlert className="h-3.5 w-3.5" />{accent}</div><h1 className="text-4xl font-semibold tracking-tight text-text">{title}</h1><p className="text-muted">{description}</p>{actions.length > 0 ? <div className="flex flex-wrap gap-3">{actions.map((action) => <Link key={action.href} href={action.href as Route}><Button variant={action.variant ?? "primary"}>{action.label}<ArrowRight className="h-4 w-4" /></Button></Link>)}</div> : null}{children}</div><Card className="w-full max-w-md"><div className="space-y-4"><div className="text-sm uppercase tracking-[0.2em] text-muted">Identity state</div><div className="text-lg font-semibold text-text">{accent}</div><div className="text-sm text-muted">This is a frontend-only screen for enterprise account and session states.</div></div></Card></div>;
}