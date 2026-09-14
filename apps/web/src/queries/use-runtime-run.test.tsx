// @vitest-environment jsdom
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { act, renderHook, waitFor } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { runtimeRunQueryKey, useAnalyzeRuntimeFinancialsMutation, useAnalyzeRuntimeValuationMutation, useCreateRedTeamReviewMutation } from "./use-runtime-run";
import type { FinancialAnalysisResult, RuntimeRun, ValuationScenarioInput, ValuationScenarios } from "@/services/research-runtime-service";

const analyze = vi.hoisted(() => vi.fn());
const createReview = vi.hoisted(() => vi.fn());
const analyzeValuation = vi.hoisted(() => vi.fn());
vi.mock("@/repositories", () => ({ researchRuntimeRepository: { analyzeFinancialsForRun: analyze, analyzeValuationScenarios: analyzeValuation, createRedTeamReview: createReview } }));

const run: RuntimeRun = {
  id: "run-1", case_id: "case-1", state: "COMPLETED", tasks: [], evidence: [], tool_executions: [], claims: [], thesis: null, memo: null,
  financial_analysis: null, red_team_reviews: [], decisions: [],
};
const analysis: FinancialAnalysisResult = {
  period: "FY2025", snapshot: { period: "FY2025", revenue: "120.00" }, input_hash: "a".repeat(64),
  revenue_growth_pct: null, gross_margin_pct: null, operating_margin_pct: null, free_cash_flow: null,
  fcf_margin_pct: null, net_cash: null, unavailable_metrics: ["revenue_growth_pct"], evidence_ids: { revenue: ["evidence-1"] }, calculation_ledger: [],
};
const valuation: ValuationScenarios = {
  id: "valuation-1", run_id: "run-1", case_id: "case-1", input_hash: "a".repeat(64), base_revenue: "100", base_revenue_evidence_ids: ["evidence-1"],
  scenarios: ["BULL", "BASE", "BEAR"].map((scenario) => ({
    scenario: scenario as "BULL" | "BASE" | "BEAR",
    assumptions: {
      name: scenario as "BULL" | "BASE" | "BEAR", revenue_growth_pct: "10", operating_margin_pct: "20", fcf_margin_pct: "15",
      discount_rate_pct: "10", terminal_growth_pct: "2", net_cash: "10", shares_outstanding: "10", evidence_ids: { revenue_growth_pct: ["evidence-1"] },
    }, projected_revenue: "110", projected_operating_income: "22", free_cash_flow: "16.5", terminal_value: "206.25", equity_value: "216.25", value_per_share: "21.625",
  })), provenance: { calculator: "test" },
};
const valuationInput: ValuationScenarioInput = {
  base_revenue: "100", base_revenue_evidence_ids: ["evidence-1"], scenarios: valuation.scenarios.map(({ assumptions }) => assumptions) as ValuationScenarioInput["scenarios"],
};

describe("useAnalyzeRuntimeFinancialsMutation", () => {
  it("projects a successful artifact into the cached run", async () => {
    analyze.mockResolvedValueOnce(analysis);
    const client = new QueryClient({ defaultOptions: { mutations: { retry: false } } });
    client.setQueryData(runtimeRunQueryKey("run-1"), run);
    const wrapper = ({ children }: { children: React.ReactNode }) => <QueryClientProvider client={client}>{children}</QueryClientProvider>;
    const { result } = renderHook(() => useAnalyzeRuntimeFinancialsMutation("run-1"), { wrapper });

    await act(async () => {
      result.current.mutate({ snapshot: { period: "FY2025", revenue: "120.00" }, evidence_ids: { revenue: ["evidence-1"] } });
    });
    await waitFor(() => expect(result.current.isSuccess).toBe(true));
    expect(client.getQueryData<RuntimeRun>(runtimeRunQueryKey("run-1"))?.financial_analysis).toEqual(analysis);
  });

  it("projects a successful red-team review from the returned run", async () => {
    const reviewedRun = { ...run, red_team_reviews: [{ id: "review-1" }] } as RuntimeRun;
    createReview.mockResolvedValueOnce(reviewedRun);
    const client = new QueryClient({ defaultOptions: { mutations: { retry: false } } });
    client.setQueryData(runtimeRunQueryKey("run-1"), run);
    const wrapper = ({ children }: { children: React.ReactNode }) => <QueryClientProvider client={client}>{children}</QueryClientProvider>;
    const { result } = renderHook(() => useCreateRedTeamReviewMutation("run-1"), { wrapper });

    await act(async () => {
      result.current.mutate({ reviewer: "Analyst", challenge: "Demand may soften.", rationale: "Counter evidence is material.", outcome: "REQUIRES_RESEARCH", evidence_ids: ["evidence-1"] });
    });
    await waitFor(() => expect(result.current.isSuccess).toBe(true));
    expect(client.getQueryData<RuntimeRun>(runtimeRunQueryKey("run-1"))).toEqual(reviewedRun);
  });
});

describe("useAnalyzeRuntimeValuationMutation", () => {
  it("projects a successful scenario artifact into the cached run", async () => {
    analyzeValuation.mockResolvedValueOnce(valuation);
    const client = new QueryClient({ defaultOptions: { mutations: { retry: false } } });
    client.setQueryData(runtimeRunQueryKey("run-1"), run);
    const wrapper = ({ children }: { children: React.ReactNode }) => <QueryClientProvider client={client}>{children}</QueryClientProvider>;
    const { result } = renderHook(() => useAnalyzeRuntimeValuationMutation("run-1"), { wrapper });

    await act(async () => { result.current.mutate(valuationInput); });
    await waitFor(() => expect(result.current.isSuccess).toBe(true));
    expect(client.getQueryData<RuntimeRun>(runtimeRunQueryKey("run-1"))?.valuation_scenarios).toEqual(valuation);
  });
});
