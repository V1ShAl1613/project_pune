"use client";

// Shared dashboard surface for the security operations center overview.
import { createColumnHelper } from "@tanstack/react-table";

import { SocShell } from "@/soc/shared/soc-shell";
import { StatPanel, SectionPanel, Grid } from "@/soc/shared/soc-panels";
import { TrendChart, WorkloadChart, DistributionChart } from "@/soc/shared/soc-chart";
import { alertData, assetData, incidentData, investigationData, iocData, riskData, threatData } from "@/soc/shared/soc-demo-data";
import { Badge } from "@/components/ui/surfaces";

const trendData = [
  { label: "Mon", value: 22 },
  { label: "Tue", value: 29 },
  { label: "Wed", value: 34 },
  { label: "Thu", value: 41 },
  { label: "Fri", value: 38 },
  { label: "Sat", value: 44 },
  { label: "Sun", value: 36 },
];

const severityData = [
  { label: "Critical", value: 9 },
  { label: "High", value: 14 },
  { label: "Medium", value: 19 },
  { label: "Low", value: 7 },
];

const workloadData = [
  { label: "SOC A", value: 18 },
  { label: "SOC B", value: 22 },
  { label: "SOC C", value: 16 },
  { label: "SOC D", value: 12 },
];

export function SocDashboardPage(): React.JSX.Element {
  return (
    <SocShell
      eyebrow="Security operations"
      title="SOC dashboard"
      description="Operational overview for alerts, incidents, cases, investigation workspaces, IOC management, threat intelligence, assets, risk, and analyst workload."
      status="real-time security operations"
      actions={[
        { label: "Open alerts", href: "/alerts" },
        { label: "Open incidents", href: "/incidents", variant: "secondary" },
      ]}
      stats={[
        { label: "Security score", value: "92", detail: "Operating target / 100" },
        { label: "Open incidents", value: String(incidentData.length), detail: "Active triage queue" },
        { label: "Critical alerts", value: String(alertData.filter((item) => item.severity === "critical").length), detail: "High-priority signals" },
        { label: "Investigations", value: String(investigationData.length), detail: "Pinned workspaces" },
      ]}
    >
      <Grid>
        <StatPanel title="Alert queue" value={String(alertData.length)} detail="Current alert backlog" />
        <StatPanel title="Incident timeline" value={String(incidentData.length)} detail="Open incident work items" />
        <StatPanel title="Asset summary" value={String(assetData.length)} detail="Critical systems under watch" />
        <StatPanel title="IOC summary" value={String(iocData.length)} detail="Observed and confirmed indicators" />
      </Grid>

      <div className="grid gap-6 xl:grid-cols-3">
        <div className="xl:col-span-2">
          <TrendChart title="Threat trends" description="Daily trend line for high-volume SOC activity." data={trendData} />
        </div>
        <DistributionChart title="Severity distribution" description="SOC severity mix across current work." data={severityData} />
      </div>

      <div className="grid gap-6 xl:grid-cols-2">
        <WorkloadChart title="Analyst workload" description="Queue allocation across the active shift." data={workloadData} />
        <SectionPanel title="Quick actions" description="Operational launch points for analysts and leads.">
          <div className="flex flex-wrap gap-2">
            <Badge tone="warning">Triage queue</Badge>
            <Badge tone="neutral">Containment review</Badge>
            <Badge tone="neutral">Escalate incident</Badge>
            <Badge tone="neutral">Assign investigator</Badge>
            <Badge tone="neutral">Create case</Badge>
          </div>
          <div className="grid gap-3 pt-2 sm:grid-cols-2">
            <div className="rounded-2xl border border-line bg-canvas p-4 text-sm text-muted">System health, response time, and SLA tracking are ready for backend metrics.</div>
            <div className="rounded-2xl border border-line bg-canvas p-4 text-sm text-muted">MITRE summary and risk summary remain frontend placeholders for routed content.</div>
          </div>
        </SectionPanel>
      </div>

      <SectionPanel title="Current operations" description="Recent threats, incidents, and risk signals in the SOC viewport.">
        <div className="grid gap-3 sm:grid-cols-2 xl:grid-cols-4">
          <div className="rounded-2xl border border-line bg-canvas p-4"><div className="text-xs uppercase tracking-wide text-muted">Alerts</div><div className="mt-2 text-2xl font-semibold">{alertData.length}</div></div>
          <div className="rounded-2xl border border-line bg-canvas p-4"><div className="text-xs uppercase tracking-wide text-muted">Threats</div><div className="mt-2 text-2xl font-semibold">{threatData.length}</div></div>
          <div className="rounded-2xl border border-line bg-canvas p-4"><div className="text-xs uppercase tracking-wide text-muted">Risk items</div><div className="mt-2 text-2xl font-semibold">{riskData.length}</div></div>
          <div className="rounded-2xl border border-line bg-canvas p-4"><div className="text-xs uppercase tracking-wide text-muted">Analyst workspaces</div><div className="mt-2 text-2xl font-semibold">{investigationData.length}</div></div>
        </div>
      </SectionPanel>
    </SocShell>
  );
}
