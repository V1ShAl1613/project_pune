// Responsive widget grid with drag-ready and resize-ready semantics.
"use client";

import { motion } from "framer-motion";

import { cn } from "@/lib/cn";
import type { DashboardWidget } from "@/dashboard/core/dashboard-models";
import { WidgetCard } from "@/dashboard/cards/dashboard-cards";

const sizeClasses: Record<DashboardWidget["size"], string> = {
  sm: "md:col-span-1",
  md: "md:col-span-2",
  lg: "md:col-span-3",
  xl: "md:col-span-4",
};

export function DashboardWidgetGrid({ widgets }: { widgets: DashboardWidget[] }): React.JSX.Element {
  return <div className="grid grid-cols-1 gap-4 md:grid-cols-4">{widgets.map((widget) => <motion.section key={widget.id} layout className={cn(sizeClasses[widget.size])}><WidgetCard title={widget.title} description={widget.description}><div className="rounded-2xl border border-dashed border-line bg-canvas p-4 text-sm text-muted">Widget container ready for live content</div></WidgetCard></motion.section>)}</div>;
}
