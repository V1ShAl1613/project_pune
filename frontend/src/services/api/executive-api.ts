import { httpClient } from "@/services/api/http-client";
import type { ExecutiveDecision, ExecutiveForecast, ExecutiveKPI, ExecutiveOverview, ExecutiveRecommendation, ExecutiveReport, ExecutiveTrend } from "@/types/executive";

export async function getExecutiveOverview(): Promise<ExecutiveOverview> {
  const { data } = await httpClient.get("/executive/overview");
  return data;
}

export async function listExecutiveKpis(): Promise<ExecutiveKPI[]> {
  const { data } = await httpClient.get("/executive/kpis");
  return data;
}

export async function listExecutiveTrends(): Promise<ExecutiveTrend[]> {
  const { data } = await httpClient.get("/executive/trends");
  return data;
}

export async function listExecutiveReports(): Promise<ExecutiveReport[]> {
  const { data } = await httpClient.get("/executive/reports");
  return data;
}

export async function getExecutiveReport(reportCode: string): Promise<ExecutiveReport> {
  const { data } = await httpClient.get(`/executive/reports/${reportCode}`);
  return data;
}

export async function listExecutiveForecasts(): Promise<ExecutiveForecast[]> {
  const { data } = await httpClient.get("/executive/forecasts");
  return data;
}

export async function listExecutiveRecommendations(): Promise<ExecutiveRecommendation[]> {
  const { data } = await httpClient.get("/executive/recommendations");
  return data;
}

export async function listExecutiveDecisions(): Promise<ExecutiveDecision[]> {
  const { data } = await httpClient.get("/executive/decisions");
  return data;
}
