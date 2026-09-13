import { describe, expect, it } from "vitest";
import { ResearchRuntimeRepository } from "./research-runtime-repository";
import { createResearchRuntimeService, type RuntimeTrace } from "@/services/research-runtime-service";

const trace: RuntimeTrace = {
  run_id: "run-1",
  case_id: "case-1",
  state: "COMPLETED",
  tasks: [{ id: "market", state: "COMPLETED", depends_on: [], missing_requirement_ids: [] }],
  evidence: { total: 1, by_qualification: { QUALIFIED: 1, NEEDS_REVIEW: 0, UNQUALIFIED: 0 }, provenance_complete: 1, provenance_incomplete: 0 },
  claims: [{ id: "claim-1", task_id: "market", status: "QUALIFIED", evidence_ids: ["evidence-1"], unresolved_evidence_ids: [] }],
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

  it("keeps synthetic mode explicit when no runtime URL is configured", async () => {
    const repository = new ResearchRuntimeRepository(createResearchRuntimeService(undefined));
    await expect(repository.getTrace("run-1")).rejects.toThrow("synthetic workspace data");
  });
});
