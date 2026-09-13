import { describe, expect, it } from "vitest";
import { ResearchRuntimeRepository } from "./research-runtime-repository";
import { createResearchRuntimeService, type InvestmentMemory, type RuntimeMemo, type RuntimeTrace } from "@/services/research-runtime-service";

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
  provenance: { generator: "test" }, generated_at: "2026-09-14T00:00:00.000Z",
};

const memory: InvestmentMemory = {
  id: "memory-1", target: "ACME", case_ids: ["case-1"], run_ids: ["run-1"], memo_ids: ["memo-1"],
  thesis_ids: ["thesis-1"], latest_run_id: "run-1", latest_thesis_id: "thesis-1", previous_thesis_id: null,
  unresolved_requirement_ids: [], decision_ids: [], updated_at: "2026-09-14T00:00:00.000Z",
};

describe("ResearchRuntimeRepository", () => {
  it("parses the runtime trace through the HTTP service boundary", async () => {
    const fetchImpl = (async () => new Response(JSON.stringify(trace), { status: 200 })) as typeof fetch;
    const repository = new ResearchRuntimeRepository(createResearchRuntimeService("http://runtime.test", fetchImpl));
    await expect(repository.getTrace("run-1")).resolves.toEqual(trace);
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
      requestBody = String(init?.body);
      return new Response(JSON.stringify({
        period: "FY2025", input_hash: "a".repeat(64), revenue_growth_pct: "20.0", gross_margin_pct: "50.0",
        operating_margin_pct: "25.0", free_cash_flow: "25", fcf_margin_pct: "20.8333", net_cash: "30", unavailable_metrics: [],
      }), { status: 200 });
    }) as typeof fetch;
    const repository = new ResearchRuntimeRepository(createResearchRuntimeService("http://runtime.test", fetchImpl));

    await expect(repository.getMemo("run-1")).resolves.toEqual(memo);
    await expect(repository.getMemory("ACME")).resolves.toEqual(memory);
    await expect(repository.analyzeFinancials({ period: "FY2025", revenue: "120.00", prior_revenue: "100.00" })).resolves.toMatchObject({ free_cash_flow: "25" });

    expect(JSON.parse(requestBody)).toMatchObject({ period: "FY2025", revenue: "120.00", prior_revenue: "100.00" });
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

  it("keeps synthetic mode explicit when no runtime URL is configured", async () => {
    const repository = new ResearchRuntimeRepository(createResearchRuntimeService(undefined));
    await expect(repository.getTrace("run-1")).rejects.toThrow("synthetic workspace data");
  });
});
