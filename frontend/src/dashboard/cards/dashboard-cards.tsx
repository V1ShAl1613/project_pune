// Reusable card surfaces for the dashboard framework.
import type { ReactNode } from "react";

import { cn } from "@/lib/cn";
import { Badge, Card } from "@/components/ui/surfaces";

type DashboardCardProps = {
  title: string;
  description?: string;
  children?: ReactNode;
  className?: string;
};

function ShellCard({ title, description, children, className }: DashboardCardProps): React.JSX.Element {
  return <Card className={cn("space-y-4", className)}><div><h3 className="text-base font-semibold text-text">{title}</h3>{description ? <p className="text-sm text-muted">{description}</p> : null}</div>{children}</Card>;
}

export function DashboardCard(props: DashboardCardProps): React.JSX.Element { return <ShellCard {...props} />; }
export function MetricCard(props: DashboardCardProps): React.JSX.Element { return <ShellCard {...props} />; }
export function StatCard(props: DashboardCardProps): React.JSX.Element { return <ShellCard {...props} />; }
export function SummaryCard(props: DashboardCardProps): React.JSX.Element { return <ShellCard {...props} />; }
export function HealthCard(props: DashboardCardProps): React.JSX.Element { return <ShellCard {...props} />; }
export function ActivityCard(props: DashboardCardProps): React.JSX.Element { return <ShellCard {...props} />; }
export function InformationCard(props: DashboardCardProps): React.JSX.Element { return <ShellCard {...props} />; }
export function StatusCard(props: DashboardCardProps): React.JSX.Element { return <ShellCard {...props} />; }
export function AlertCard(props: DashboardCardProps): React.JSX.Element { return <ShellCard {...props} />; }
export function WidgetCard(props: DashboardCardProps): React.JSX.Element { return <ShellCard {...props} />; }
export function ContainerCard(props: DashboardCardProps): React.JSX.Element { return <ShellCard {...props} />; }
export function GlassCard(props: DashboardCardProps): React.JSX.Element { return <ShellCard {...props} className={cn("bg-panel/80 backdrop-blur-xl", props.className)} />; }
export function HoverCard(props: DashboardCardProps): React.JSX.Element { return <ShellCard {...props} className={cn("transition hover:-translate-y-0.5 hover:shadow-soft", props.className)} />; }

export function ExpandableCard({ title, description, children, className }: DashboardCardProps): React.JSX.Element {
  return <details className={cn("rounded-2xl border border-line bg-panel p-5", className)}><summary className="cursor-pointer list-none text-base font-semibold text-text">{title}</summary>{description ? <p className="mt-2 text-sm text-muted">{description}</p> : null}<div className="mt-4">{children}</div></details>;
}

export function CardStatus({ status }: { status: string }): React.JSX.Element {
  return <Badge tone={status === "active" ? "success" : status === "warning" ? "warning" : status === "error" ? "danger" : "neutral"}>{status}</Badge>;
}
