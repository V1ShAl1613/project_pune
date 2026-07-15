"use client";

// Reusable timeline route for incidents, cases, alerts, threats, evidence, IOC, investigation, and activity views.
import { SocShell } from "@/soc/shared/soc-shell";
import { SectionPanel } from "@/soc/shared/soc-panels";

const timelineItems = [
  { title: "08:42", description: "Alert escalated from Open to Investigating." },
  { title: "08:15", description: "IOC added to watchlist with high confidence." },
  { title: "07:55", description: "Incident assignment updated for SOC B." },
  { title: "07:10", description: "Evidence tagged and integrity verified." },
];

export default function TimelinePage(): React.JSX.Element {
  return <SocShell eyebrow="Timeline" title="Activity Timeline" description="Incident timeline, case timeline, alert timeline, threat timeline, evidence timeline, IOC timeline, investigation timeline, and activity timeline reuse this view." status="event chronology" stats={[{ label: "Events", value: String(timelineItems.length), detail: "Visible timeline entries" }, { label: "Coverage", value: "All", detail: "Shared chronology surface" }]}><SectionPanel title="Chronology" description="Frontend-only event stream with reusable presentation."><div className="space-y-3">{timelineItems.map((item) => <div key={item.title} className="rounded-2xl border border-line bg-canvas p-4"><div className="text-sm font-semibold text-text">{item.title}</div><div className="text-sm text-muted">{item.description}</div></div>)}</div></SectionPanel></SocShell>;
}
