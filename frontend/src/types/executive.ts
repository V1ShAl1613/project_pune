export type ExecutiveKPI = {
  code: string;
  label: string;
  value: string;
  unit?: string | null;
  delta?: string | null;
  direction: "up" | "flat" | "down";
  benchmark?: string | null;
  detail: string;
  category: string;
};

export type ExecutiveTrendPoint = {
  label: string;
  value: number;
};

export type ExecutiveTrend = {
  code: string;
  label: string;
  category: string;
  summary: string;
  points: ExecutiveTrendPoint[];
};

export type ExecutiveReport = {
  report_code: string;
  title: string;
  audience: string;
  owner: string;
  status: string;
  score: number;
  summary: string;
  highlights: string[];
  period_label: string;
  published_at?: string | null;
  report_metadata: Record<string, unknown>;
};

export type ExecutiveForecast = {
  scenario: string;
  horizon: string;
  confidence: number;
  projected_value: string;
  lower_bound: string;
  upper_bound: string;
  drivers: string[];
  forecast_metadata: Record<string, unknown>;
};

export type ExecutiveRecommendation = {
  priority_rank: number;
  priority: "critical" | "high" | "medium" | "low";
  title: string;
  action: string;
  owner: string;
  horizon: string;
  expected_impact: string;
  value_score: number;
  evidence: string[];
  recommendation_metadata: Record<string, unknown>;
};

export type ExecutiveDecision = {
  decision_code: string;
  topic: string;
  decision: string;
  status: string;
  approved_by?: string | null;
  rationale: string;
  impact: string;
  next_review_at?: string | null;
  decision_metadata: Record<string, unknown>;
};

export type ExecutiveSummary = {
  title: string;
  narrative: string;
  operating_status: string;
  health_score: number;
  decision_velocity: string;
  risk_posture: string;
};

export type ExecutiveOverview = {
  generated_at: string;
  summary: ExecutiveSummary;
  kpis: ExecutiveKPI[];
  trends: ExecutiveTrend[];
  reports: ExecutiveReport[];
  forecasts: ExecutiveForecast[];
  recommendations: ExecutiveRecommendation[];
  decisions: ExecutiveDecision[];
};
