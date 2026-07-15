"use client";

// Analyst workbench route for personal queues, notes, bookmarks, and workspace preferences.
import { SocShell } from "@/soc/shared/soc-shell";
import { SectionPanel, Grid } from "@/soc/shared/soc-panels";

export default function WorkbenchPage(): React.JSX.Element {
  return <SocShell eyebrow="Analyst workspace" title="Workbench" description="My alerts, incidents, cases, assigned tasks, recent activity, bookmarks, pinned investigations, personal notes, and workspace preferences." status="analyst desktop" stats={[{ label: "Pinned investigations", value: "2", detail: "Saved workspaces" }, { label: "Assigned tasks", value: "6", detail: "Queue items" }]}><Grid><SectionPanel title="My alerts" description="Personal triage queue."><div className="text-sm text-muted">Alert routing and prioritization surfaces are ready.</div></SectionPanel><SectionPanel title="My incidents" description="Incident ownership and handoff."><div className="text-sm text-muted">Ownership, notes, and status changes are frontend-ready.</div></SectionPanel><SectionPanel title="My cases" description="Structured investigations and task tracking."><div className="text-sm text-muted">Case assignment and personal queue views are ready.</div></SectionPanel><SectionPanel title="Workspace preferences" description="User preferences for analyst ergonomics."><div className="text-sm text-muted">Layout, theme, and density preferences are surfaced here.</div></SectionPanel></Grid></SocShell>;
}
