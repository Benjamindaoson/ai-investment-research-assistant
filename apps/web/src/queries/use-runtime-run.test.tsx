// @vitest-environment jsdom
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { act, renderHook, waitFor } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { runtimeCaseRunsQueryKey, runtimeEvaluationQueryKey, runtimeEventsQueryKey, runtimeHealthQueryKey, runtimeIcReviewsQueryKey, runtimeRefreshInterval, runtimeRunQueryKey, useAnalyzeRuntimeFinancialsMutation, useAnalyzeRuntimeValuationMutation, useCreateInvestmentCommitteeReviewMutation, useCreateRedTeamReviewMutation, useCreateRuntimeRerunMutation, useRuntimeCaseRunsQuery, useRuntimeEvaluationQuery, useRuntimeEventsQuery, useRuntimeHealthQuery } from "./use-runtime-run";
import type { FinancialAnalysisResult, RuntimeEvent, RuntimeHealth, RuntimeRun, ValuationScenarioInput, ValuationScenarios } from "@/services/research-runtime-service";

const analyze = vi.hoisted(() => vi.fn());
const createReview = vi.hoisted(() => vi.fn());
const createIcReview = vi.hoisted(() => vi.fn());
const analyzeValuation = vi.hoisted(() => vi.fn());
const getCaseRuns = vi.hoisted(() => vi.fn());
const createCaseRun = vi.hoisted(() => vi.fn());
const getEvaluation = vi.hoisted(() => vi.fn());
const getEvents = vi.hoisted(() => vi.fn());
const getHealth = vi.hoisted(() => vi.fn());
vi.mock("@/repositories", () => ({ researchRuntimeRepository: { analyzeFinancialsForRun: analyze, analyzeValuationScenarios: analyzeValuation, createRedTeamReview: createReview, createInvestmentCommitteeReview: createIcReview, getCaseRuns, createCaseRun, getEvaluation, getEvents, getHealth } }));

const run: RuntimeRun = {
  id: "run-1", case_id: "case-1", state: "COMPLETED", tasks: [], evidence: [], tool_executions: [], claims: [], thesis: null, memo: null,
  financial_analysis: null, red_team_reviews: [], ic_reviews: [], decisions: [],
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

describe("runtimeRefreshInterval", () => {
  it("refreshes active runs and stops at terminal states", () => {
    expect(runtimeRefreshInterval("CREATED")).toBe(2000);
    expect(runtimeRefreshInterval("RUNNING")).toBe(2000);
    expect(runtimeRefreshInterval("VERIFYING")).toBe(2000);
    expect(runtimeRefreshInterval("COMPLETED")).toBe(false);
    expect(runtimeRefreshInterval("BLOCKED")).toBe(false);
    expect(runtimeRefreshInterval(undefined)).toBe(false);
  });
});

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

describe("useRuntimeCaseRunsQuery", () => {
  it("loads case history into its own query cache", async () => {
    getCaseRuns.mockResolvedValueOnce([run]);
    const client = new QueryClient({ defaultOptions: { queries: { retry: false } } });
    const wrapper = ({ children }: { children: React.ReactNode }) => <QueryClientProvider client={client}>{children}</QueryClientProvider>;
    const { result } = renderHook(() => useRuntimeCaseRunsQuery("case-1"), { wrapper });

    await waitFor(() => expect(result.current.isSuccess).toBe(true));
    expect(result.current.data).toEqual([run]);
    expect(client.getQueryData(runtimeCaseRunsQueryKey("case-1"))).toEqual([run]);
  });
});

describe("useCreateInvestmentCommitteeReviewMutation", () => {
  it("projects the server review and invalidates the review query", async () => {
    const reviewedRun = { ...run, ic_reviews: [{ id: "ic-review-1" }] } as RuntimeRun;
    createIcReview.mockResolvedValueOnce(reviewedRun);
    const client = new QueryClient({ defaultOptions: { mutations: { retry: false } } });
    client.setQueryData(runtimeRunQueryKey("run-1"), run);
    client.setQueryData(runtimeIcReviewsQueryKey("run-1"), []);
    const wrapper = ({ children }: { children: React.ReactNode }) => <QueryClientProvider client={client}>{children}</QueryClientProvider>;
    const { result } = renderHook(() => useCreateInvestmentCommitteeReviewMutation("run-1"), { wrapper });

    await act(async () => { await result.current.mutateAsync({ role: "FINANCIAL", reviewer: "CFO", position: "MIXED", recommendation: "HOLD", rationale: "Margins need review.", evidence_ids: ["evidence-1"] }); });
    expect(client.getQueryData<RuntimeRun>(runtimeRunQueryKey("run-1"))).toEqual(reviewedRun);
    expect(client.getQueryState(runtimeIcReviewsQueryKey("run-1"))).toBeDefined();
  });
});

describe("useCreateRuntimeRerunMutation", () => {
  it("invalidates case history after the runtime creates a new run", async () => {
    createCaseRun.mockResolvedValueOnce({ case_id: "case-1", run_id: "run-2" });
    const client = new QueryClient({ defaultOptions: { mutations: { retry: false } } });
    client.setQueryData(runtimeCaseRunsQueryKey("case-1"), [run]);
    const wrapper = ({ children }: { children: React.ReactNode }) => <QueryClientProvider client={client}>{children}</QueryClientProvider>;
    const { result } = renderHook(() => useCreateRuntimeRerunMutation("case-1"), { wrapper });

    await act(async () => { await result.current.mutateAsync(); });
    expect(createCaseRun).toHaveBeenCalledWith("case-1");
    expect(client.getQueryState(runtimeCaseRunsQueryKey("case-1"))).toBeDefined();
  });
});

describe("useRuntimeEvaluationQuery", () => {
  it("keeps the evaluation artifact separate from the run cache", async () => {
    const evaluation = { id: "evaluation-1", case_id: "case-1", run_id: "run-1", evaluator: "scorer-v1", case_hash: "a".repeat(64), passed: true, checks: [{ name: "memo", status: "PASS", detail: "Memo is complete." }], evaluated_at: "2026-09-14T00:00:00.000Z" };
    getEvaluation.mockResolvedValueOnce(evaluation);
    const client = new QueryClient({ defaultOptions: { queries: { retry: false } } });
    const wrapper = ({ children }: { children: React.ReactNode }) => <QueryClientProvider client={client}>{children}</QueryClientProvider>;
    const { result } = renderHook(() => useRuntimeEvaluationQuery("run-1"), { wrapper });

    await waitFor(() => expect(result.current.isSuccess).toBe(true));
    expect(client.getQueryData(runtimeEvaluationQueryKey("run-1"))).toEqual(evaluation);
  });
});

describe("useRuntimeEventsQuery", () => {
  it("loads events and uses active-run refresh semantics", async () => {
    const events: RuntimeEvent[] = [{ seq: 1, run_id: "run-1", event_type: "RUN_CREATED", payload: {}, occurred_at: "2026-09-14T00:00:00.000Z" }];
    getEvents.mockResolvedValueOnce(events);
    const client = new QueryClient({ defaultOptions: { queries: { retry: false } } });
    const wrapper = ({ children }: { children: React.ReactNode }) => <QueryClientProvider client={client}>{children}</QueryClientProvider>;
    const { result } = renderHook(() => useRuntimeEventsQuery("run-1", "RUNNING"), { wrapper });

    await waitFor(() => expect(result.current.isSuccess).toBe(true));
    expect(result.current.data).toEqual(events);
    expect(client.getQueryData(runtimeEventsQueryKey("run-1"))).toEqual(events);
  });

  it("stops polling for terminal runs", () => {
    expect(runtimeRefreshInterval("COMPLETED")).toBe(false);
  });
});

describe("useRuntimeHealthQuery", () => {
  it("loads provider readiness independently from run state", async () => {
    const health: RuntimeHealth = { status: "ok", service: "runtime", evidence_mode: "LIVE_EXTERNAL", evidence_provider: "finevidence-http", planner: "planner · v1", synthesizer: "synth · v1", tools: ["external-evidence"] };
    getHealth.mockResolvedValueOnce(health);
    const client = new QueryClient({ defaultOptions: { queries: { retry: false } } });
    const wrapper = ({ children }: { children: React.ReactNode }) => <QueryClientProvider client={client}>{children}</QueryClientProvider>;
    const { result } = renderHook(() => useRuntimeHealthQuery(true), { wrapper });

    await waitFor(() => expect(result.current.isSuccess).toBe(true));
    expect(result.current.data).toEqual(health);
    expect(client.getQueryData(runtimeHealthQueryKey)).toEqual(health);
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
