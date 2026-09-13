import { describe, expect, it } from "vitest";
import { ResearchRuntimeRepository } from "./research-runtime-repository";
import { createResearchRuntimeService, type InvestmentMemory, type RuntimeMemo, type RuntimeRun, type RuntimeTrace } from "@/services/research-runtime-service";

const trace: RuntimeTrace = {
  run_id: "run-1",
  case_id: "case-1",
  state: "COMPLETED",
  tasks: [{ id: "market", state: "COMPLETED", depends_on: [], missing_requirement_ids: [] }],
  evidence: { total: 1, by_qualification: { QUALIFIED: 1, NEEDS_REVIEW: 0, UNQUALIFIED: 0 }, provenance_complete: 1, provenance_incomplete: 0 },
  claims: [{ id: "claim-1", task_id: "market", status: "QUALIFIED", evidence_ids: ["evidence-1"], unresolved_evidence_ids: [] }],
};

const memo: RuntimeMemo = {
  id: "memo-1", run_id: "run-1", case_id: "case-1", title: "ACME research memo", status: "READY_FOR_REVIEW",
  executive_summary: "Observed evidence remains reviewable.", thesis_id: "thesis-1", claim_ids: ["claim-1"],
  evidence_ids: ["evidence-1"], counter_evidence_ids: ["evidence-2"], unresolved_requirement_ids: [],
  sections: [{ section_key: "thesis", title: "Investment thesis", body: "Observed thesis.", claim_ids: ["claim-1"], evidence_ids: ["evidence-1"], unresolved_requirement_ids: [] }],
  provenance: { generator: "test" }, generated_at: "2026-09-14T00:00:00.000Z",
};

const memory: InvestmentMemory = {
  id: "memory-1", target: "ACME", case_ids: ["case-1"], run_ids: ["run-1"], memo_ids: ["memo-1"],
  thesis_ids: ["thesis-1"], latest_run_id: "run-1", latest_thesis_id: "thesis-1", previous_thesis_id: null,
  latest_thesis_delta: {
    previous_thesis_id: "thesis-0", current_thesis_id: "thesis-1", qualified_evidence_delta: -1,
    counter_conflicting_evidence_delta: 1, unresolved_requirement_delta: 1,
    summary: "Observed count change; this is not a confidence estimate or investment advice.",
    observed_at: "2026-09-14T00:00:00.000Z",
  },
  unresolved_requirement_ids: [], decision_ids: [], updated_at: "2026-09-14T00:00:00.000Z",
};

const run: RuntimeRun = {
  id: "run-1", case_id: "case-1", state: "CREATED", tasks: [{ id: "market", title: "Market", state: "PENDING" }],
  evidence: [], tool_executions: [], claims: [], thesis: null, memo: null, financial_analysis: null, red_team_reviews: [], decisions: [],
};

describe("ResearchRuntimeRepository", () => {
  it("parses the runtime trace through the HTTP service boundary", async () => {
    const fetchImpl = (async () => new Response(JSON.stringify(trace), { status: 200 })) as typeof fetch;
    const repository = new ResearchRuntimeRepository(createResearchRuntimeService("http://runtime.test", fetchImpl));
    await expect(repository.getTrace("run-1")).resolves.toEqual(trace);
  });

  it("creates, reads, and executes a runtime run through the repository", async () => {
    const fetchImpl = (async (input) => {
      const url = String(input);
      if (url.endsWith("/research-cases")) return new Response(JSON.stringify({ case_id: "case-1", run_id: "run-1" }), { status: 201 });
      return new Response(JSON.stringify({ ...run, state: url.endsWith("/execute") ? "COMPLETED" : "CREATED" }), { status: 200 });
    }) as typeof fetch;
    const repository = new ResearchRuntimeRepository(createResearchRuntimeService("http://runtime.test", fetchImpl));

    await expect(repository.createCase({ question: "Assess ACME risk", target: "ACME" })).resolves.toEqual({ case_id: "case-1", run_id: "run-1" });
    await expect(repository.getRun("run-1")).resolves.toMatchObject({ state: "CREATED" });
    await expect(repository.executeRun("run-1")).resolves.toMatchObject({ state: "COMPLETED" });
  });

  it("preserves detailed claims from a completed run", async () => {
    const detailedRun = { ...run, state: "COMPLETED", claims: [{
      id: "claim-1", task_id: "market", statement: "Market evidence qualifies.", status: "QUALIFIED",
      confidence: 1, evidence_ids: ["evidence-1"],
    }] };
    const fetchImpl = (async () => new Response(JSON.stringify(detailedRun), { status: 200 })) as typeof fetch;
    const repository = new ResearchRuntimeRepository(createResearchRuntimeService("http://runtime.test", fetchImpl));

    await expect(repository.getRun("run-1")).resolves.toMatchObject({ claims: detailedRun.claims });
  });

  it("preserves the detailed task contract from a completed run", async () => {
    const detailedRun = { ...run, tasks: [{
      id: "market", title: "Market", state: "COMPLETED", purpose: "Assess market structure.", depends_on: [], tool_name: "research",
      evidence_requirements: [{ id: "market-signal", description: "Market signal", minimum_records: 1, required_stances: ["SUPPORTING"] }],
    }] };
    const fetchImpl = (async () => new Response(JSON.stringify(detailedRun), { status: 200 })) as typeof fetch;
    const repository = new ResearchRuntimeRepository(createResearchRuntimeService("http://runtime.test", fetchImpl));

    await expect(repository.getRun("run-1")).resolves.toMatchObject({ tasks: detailedRun.tasks });
  });

  it("preserves tool execution receipts from a completed run", async () => {
    const detailedRun = { ...run, tool_executions: [{
      id: "tool-1", task_id: "market", tool_name: "research", status: "SUCCEEDED", result_hash: "a".repeat(16),
      started_at: "2026-09-14T00:00:00.000Z", completed_at: "2026-09-14T00:00:01.000Z",
    }] };
    const fetchImpl = (async () => new Response(JSON.stringify(detailedRun), { status: 200 })) as typeof fetch;
    const repository = new ResearchRuntimeRepository(createResearchRuntimeService("http://runtime.test", fetchImpl));

    await expect(repository.getRun("run-1")).resolves.toMatchObject({ tool_executions: detailedRun.tool_executions });
  });

  it("posts an explicit research mandate at the runtime boundary", async () => {
    let requestBody = "";
    const fetchImpl = (async (_input, init) => {
      requestBody = String(init?.body);
      return new Response(JSON.stringify({ case_id: "case-1", run_id: "run-1" }), { status: 201 });
    }) as typeof fetch;
    const repository = new ResearchRuntimeRepository(createResearchRuntimeService("http://runtime.test", fetchImpl));

    await repository.createCase({
      question: "Assess ACME before acquisition",
      target: "ACME",
      mandate: {
        decision_type: "DUE_DILIGENCE",
        time_horizon: "36 months",
        materiality: "HIGH",
        required_outputs: ["investment memo", "valuation sensitivity"],
        constraints: ["Exclude management projections"],
      },
    });

    expect(JSON.parse(requestBody)).toEqual({
      question: "Assess ACME before acquisition",
      target: "ACME",
      mandate: {
        decision_type: "DUE_DILIGENCE",
        time_horizon: "36 months",
        materiality: "HIGH",
        required_outputs: ["investment memo", "valuation sensitivity"],
        constraints: ["Exclude management projections"],
      },
    });
  });

  it("replans a partial run through the typed repository boundary", async () => {
    let requestUrl = "";
    let requestMethod = "";
    const fetchImpl = (async (input, init) => {
      requestUrl = String(input);
      requestMethod = String(init?.method);
      return new Response(JSON.stringify({ ...run, state: "CREATED" }), { status: 200 });
    }) as typeof fetch;
    const repository = new ResearchRuntimeRepository(createResearchRuntimeService("http://runtime.test", fetchImpl));

    await expect(repository.replanRun("run-1")).resolves.toMatchObject({ id: "run-1", state: "CREATED" });
    expect(requestUrl).toBe("http://runtime.test/api/v1/research-runs/run-1/replan");
    expect(requestMethod).toBe("POST");
  });

  it("surfaces runtime HTTP errors", async () => {
    const fetchImpl = (async () => new Response("unavailable", { status: 503 })) as typeof fetch;
    const repository = new ResearchRuntimeRepository(createResearchRuntimeService("http://runtime.test", fetchImpl));
    await expect(repository.getTrace("run-1")).rejects.toThrow("HTTP 503");
  });

  it("parses memo and memory and preserves decimal strings for backend analysis", async () => {
    let requestBody = "";
    const fetchImpl = (async (input, init) => {
      const url = String(input);
      if (url.endsWith("/memo")) return new Response(JSON.stringify(memo), { status: 200 });
      if (url.endsWith("/investment-memory/ACME")) return new Response(JSON.stringify(memory), { status: 200 });
      if (url.endsWith("/research-runs/run-1/memory")) return new Response(JSON.stringify(memory), { status: 200 });
      requestBody = String(init?.body);
      return new Response(JSON.stringify({
        period: "FY2025", snapshot: { period: "FY2025", revenue: "120.00", prior_revenue: "100.00" },
        input_hash: "a".repeat(64), revenue_growth_pct: "20.0", gross_margin_pct: "50.0",
        operating_margin_pct: "25.0", free_cash_flow: "25", fcf_margin_pct: "20.8333", net_cash: "30", unavailable_metrics: [],
      }), { status: 200 });
    }) as typeof fetch;
    const repository = new ResearchRuntimeRepository(createResearchRuntimeService("http://runtime.test", fetchImpl));

    await expect(repository.getMemo("run-1")).resolves.toEqual(memo);
    await expect(repository.getMemory("ACME")).resolves.toEqual(memory);
    await expect(repository.getMemoryForRun("run-1")).resolves.toEqual(memory);
    await expect(repository.analyzeFinancials({ period: "FY2025", revenue: "120.00", prior_revenue: "100.00" })).resolves.toMatchObject({ free_cash_flow: "25" });

    expect(JSON.parse(requestBody)).toMatchObject({ period: "FY2025", revenue: "120.00", prior_revenue: "100.00" });
  });

  it("posts run-scoped financial analysis with field-level evidence links", async () => {
    let requestBody = "";
    let requestUrl = "";
    const fetchImpl = (async (input, init) => {
      requestUrl = String(input);
      requestBody = String(init?.body);
      return new Response(JSON.stringify({
        period: "FY2025", snapshot: { period: "FY2025", revenue: "120.00", prior_revenue: "100.00" },
        input_hash: "a".repeat(64), revenue_growth_pct: "20.0",
        gross_margin_pct: null, operating_margin_pct: null, free_cash_flow: null,
        fcf_margin_pct: null, net_cash: null, unavailable_metrics: ["gross_margin_pct"],
        evidence_ids: { revenue: ["evidence-1"], prior_revenue: ["evidence-1"] },
      }), { status: 200 });
    }) as typeof fetch;
    const repository = new ResearchRuntimeRepository(createResearchRuntimeService("http://runtime.test", fetchImpl));

    await expect(repository.analyzeFinancialsForRun("run/1", {
      snapshot: { period: "FY2025", revenue: "120.00", prior_revenue: "100.00" },
      evidence_ids: { revenue: ["evidence-1"], prior_revenue: ["evidence-1"] },
    })).resolves.toMatchObject({ evidence_ids: { revenue: ["evidence-1"] } });
    expect(requestUrl).toBe("http://runtime.test/api/v1/research-runs/run%2F1/financial-analysis");
    expect(JSON.parse(requestBody)).toEqual({
      snapshot: { period: "FY2025", revenue: "120.00", prior_revenue: "100.00" },
      evidence_ids: { revenue: ["evidence-1"], prior_revenue: ["evidence-1"] },
    });
  });

  it("reads a persisted run-scoped financial analysis artifact", async () => {
    const artifact = {
      period: "FY2025", snapshot: { period: "FY2025", revenue: "120.00", prior_revenue: "100.00" },
      input_hash: "a".repeat(64), revenue_growth_pct: "20.0",
      gross_margin_pct: null, operating_margin_pct: null, free_cash_flow: null,
      fcf_margin_pct: null, net_cash: null, unavailable_metrics: ["gross_margin_pct"],
      evidence_ids: { revenue: ["evidence-1"], prior_revenue: ["evidence-1"] },
      calculation_ledger: [],
    };
    let requestUrl = "";
    const fetchImpl = (async (input) => {
      requestUrl = String(input);
      return new Response(JSON.stringify(artifact), { status: 200 });
    }) as typeof fetch;
    const repository = new ResearchRuntimeRepository(createResearchRuntimeService("http://runtime.test", fetchImpl));

    await expect(repository.getFinancialAnalysisForRun("run-1")).resolves.toEqual(artifact);
    expect(requestUrl).toBe("http://runtime.test/api/v1/research-runs/run-1/financial-analysis");
  });

  it("creates and lists red-team reviews through the typed service boundary", async () => {
    const review = {
      id: "review-1", run_id: "run-1", thesis_id: "thesis-1", reviewer: "Analyst",
      challenge: "Demand may soften.", evidence_ids: ["evidence-2"], outcome: "REQUIRES_RESEARCH",
      rationale: "Counter evidence is material.", created_at: "2026-09-14T00:00:00.000Z",
    };
    let postBody = "";
    const fetchImpl = (async (input, init) => {
      const url = String(input);
      if (init?.method === "POST") postBody = String(init.body ?? "");
      if (url.endsWith("/red-team-reviews") && init?.method !== "POST") return new Response(JSON.stringify([review]), { status: 200 });
      return new Response(JSON.stringify({ ...run, red_team_reviews: [review] }), { status: 200 });
    }) as typeof fetch;
    const repository = new ResearchRuntimeRepository(createResearchRuntimeService("http://runtime.test", fetchImpl));

    await expect(repository.createRedTeamReview("run-1", {
      reviewer: "Analyst", challenge: "Demand may soften.", evidence_ids: ["evidence-2"],
      outcome: "REQUIRES_RESEARCH", rationale: "Counter evidence is material.",
    })).resolves.toMatchObject({ red_team_reviews: [{ id: "review-1" }] });
    await expect(repository.getRedTeamReviews("run-1")).resolves.toEqual([review]);
    expect(JSON.parse(postBody)).toEqual({
      reviewer: "Analyst", challenge: "Demand may soften.", evidence_ids: ["evidence-2"],
      outcome: "REQUIRES_RESEARCH", rationale: "Counter evidence is material.",
    });
  });

  it("records a thesis decision and parses an older run without decision history", async () => {
    let requestBody = "";
    const fetchImpl = (async (_input, init) => {
      requestBody = String(init?.body);
      return new Response(JSON.stringify({ ...run, thesis: { id: "thesis-1", statement: "Thesis", bull: "Bull", base: "Base", bear: "Bear", claim_ids: [], review_status: "APPROVED" }, decisions: [{ id: "decision-1", actor: "Analyst", action: "APPROVE_THESIS", target_id: "thesis-1", rationale: "Evidence reviewed.", created_at: "2026-09-14T00:00:00.000Z" }] }), { status: 200 });
    }) as typeof fetch;
    const repository = new ResearchRuntimeRepository(createResearchRuntimeService("http://runtime.test", fetchImpl));

    await expect(repository.recordDecision("run-1", {
      actor: "Analyst", action: "APPROVE_THESIS", target_id: "thesis-1", rationale: "Evidence reviewed.",
    })).resolves.toMatchObject({ decisions: [{ id: "decision-1", action: "APPROVE_THESIS" }] });
    expect(JSON.parse(requestBody)).toEqual({ actor: "Analyst", action: "APPROVE_THESIS", target_id: "thesis-1", rationale: "Evidence reviewed." });

    const oldRunFetch = (async () => new Response(JSON.stringify({ ...run, decisions: undefined }), { status: 200 })) as typeof fetch;
    await expect(new ResearchRuntimeRepository(createResearchRuntimeService("http://runtime.test", oldRunFetch)).getRun("run-1")).resolves.toMatchObject({ decisions: [] });
  });

  it("parses the validated plan mandate from a runtime run", async () => {
    const fetchImpl = (async () => new Response(JSON.stringify({ ...run, plan: {
      id: "plan-1", case_id: "case-1", question: "Assess ACME", planner_name: "planner", planner_version: "v1",
      input_hash: "a".repeat(64), status: "VALIDATED",
      mandate: { decision_type: "SCREENING", time_horizon: "90 days", materiality: "LOW", required_outputs: ["screening note"], constraints: [] },
    } }), { status: 200 })) as typeof fetch;
    await expect(new ResearchRuntimeRepository(createResearchRuntimeService("http://runtime.test", fetchImpl)).getRun("run-1")).resolves.toMatchObject({ plan: { planner_name: "planner", mandate: { decision_type: "SCREENING" } } });
  });

  it("posts a cancellation reason and validates the terminal run state", async () => {
    let request: RequestInit | undefined;
    const fetchImpl = (async (_input, init) => {
      request = init;
      return new Response(JSON.stringify({ id: "run-1", case_id: "case-1", state: "CANCELLED" }), { status: 200 });
    }) as typeof fetch;
    const repository = new ResearchRuntimeRepository(createResearchRuntimeService("http://runtime.test", fetchImpl));

    await expect(repository.cancelRun("run-1", "Analyst stopped the run")).resolves.toEqual({ id: "run-1", case_id: "case-1", state: "CANCELLED" });
    expect(JSON.parse(String(request?.body))).toEqual({ reason: "Analyst stopped the run" });
  });

  it("rejects an invalid cancellation response", async () => {
    const fetchImpl = (async () => new Response(JSON.stringify({ id: "run-1", state: "COMPLETE" }), { status: 200 })) as typeof fetch;
    const repository = new ResearchRuntimeRepository(createResearchRuntimeService("http://runtime.test", fetchImpl));
    await expect(repository.cancelRun("run-1", "Stop now")).rejects.toThrow();
  });

  it("surfaces cancellation HTTP errors", async () => {
    const fetchImpl = (async () => new Response("busy", { status: 409 })) as typeof fetch;
    const repository = new ResearchRuntimeRepository(createResearchRuntimeService("http://runtime.test", fetchImpl));
    await expect(repository.cancelRun("run-1", "Stop now")).rejects.toThrow("HTTP 409");
  });

  it("rejects an invalid memo response at the Zod boundary", async () => {
    const fetchImpl = (async () => new Response(JSON.stringify({ id: "memo-1" }), { status: 200 })) as typeof fetch;
    const repository = new ResearchRuntimeRepository(createResearchRuntimeService("http://runtime.test", fetchImpl));
    await expect(repository.getMemo("run-1")).rejects.toThrow();
  });

  it("rejects a memo with an unsupported structured section", async () => {
    const invalid = { ...memo, sections: [{ ...memo.sections[0], section_key: "valuation" }] };
    const fetchImpl = (async () => new Response(JSON.stringify(invalid), { status: 200 })) as typeof fetch;
    const repository = new ResearchRuntimeRepository(createResearchRuntimeService("http://runtime.test", fetchImpl));
    await expect(repository.getMemo("run-1")).rejects.toThrow();
  });

  it("keeps synthetic mode explicit when no runtime URL is configured", async () => {
    const repository = new ResearchRuntimeRepository(createResearchRuntimeService(undefined));
    await expect(repository.getTrace("run-1")).rejects.toThrow("synthetic workspace data");
  });
});
