// Shared module shell used by the dashboard placeholder routes.
import Link from "next/link";
import type { Route } from "next";

import { Button } from "@/components/ui/controls";
import { DashboardCard } from "@/dashboard/cards/dashboard-cards";
import { DashboardShell } from "@/dashboard/layouts/dashboard-shell";

export function ModuleShell({ title, description, href }: { title: string; description: string; href: string }): React.JSX.Element {
  return <DashboardShell><DashboardCard title={title} description={description}><div className="space-y-4 rounded-2xl border border-dashed border-line bg-canvas p-6 text-sm text-muted"><p>This is a dashboard framework shell for future module composition.</p><div className="flex flex-wrap gap-3"><Link href={href as Route}><Button>Open module shell</Button></Link><Link href="/dashboard"><Button variant="secondary">Return to dashboard</Button></Link></div></div></DashboardCard></DashboardShell>;
}
