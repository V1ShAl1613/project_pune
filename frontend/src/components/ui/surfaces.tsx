"use client";

import { cn } from "@/lib/cn";

export function Card({ className, children }: { className?: string; children: React.ReactNode }): React.JSX.Element {
  return <section className={cn("rounded-2xl border border-line bg-panel p-6 shadow-soft", className)}>{children}</section>;
}

export function Avatar({ name, src, className }: { name: string; src?: string | null; className?: string }): React.JSX.Element {
  return src ? (
    <img alt={name} className={cn("h-10 w-10 rounded-full object-cover", className)} src={src} />
  ) : (
    <div className={cn("flex h-10 w-10 items-center justify-center rounded-full bg-primary text-sm font-semibold text-primary-foreground", className)}>{name.slice(0, 1).toUpperCase()}</div>
  );
}

export function Badge({ children, tone = "neutral" }: { children: React.ReactNode; tone?: "neutral" | "success" | "warning" | "danger" }): React.JSX.Element {
  return <span className={cn("inline-flex items-center rounded-full px-2.5 py-1 text-xs font-medium", tone === "neutral" && "bg-muted text-text", tone === "success" && "bg-success/15 text-success", tone === "warning" && "bg-warning/15 text-warning", tone === "danger" && "bg-danger/15 text-danger")}>{children}</span>;
}

export function StatusBadge({ status }: { status: string }): React.JSX.Element {
  const tone = status === "active" ? "success" : status === "pending" ? "warning" : status === "suspended" ? "danger" : "neutral";
  return <Badge tone={tone}>{status}</Badge>;
}

export function Alert({ title, description }: { title: string; description?: string }): React.JSX.Element {
  return <div className="rounded-2xl border border-line bg-panel p-4"><div className="text-sm font-semibold text-text">{title}</div>{description ? <div className="mt-1 text-sm text-muted">{description}</div> : null}</div>;
}

export function Spinner({ label = "Loading" }: { label?: string }): React.JSX.Element {
  return <div className="inline-flex items-center gap-2 text-sm text-muted"><span className="h-4 w-4 animate-spin rounded-full border-2 border-line border-t-primary" />{label}</div>;
}
