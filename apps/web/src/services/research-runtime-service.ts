import { z } from "zod";

const runtimeTaskTraceSchema = z.object({
  id: z.string(),
  state: z.enum(["PENDING", "RUNNING", "COMPLETED", "FAILED"]),
  depends_on: z.array(z.string()),
  missing_requirement_ids: z.array(z.string()),
});

const runtimeTraceSchema = z.object({
  run_id: z.string(),
  case_id: z.string(),
  state: z.enum(["CREATED", "RUNNING", "VERIFYING", "COMPLETED", "PARTIAL", "FAILED", "CANCELLED"]),
  tasks: z.array(runtimeTaskTraceSchema),
  evidence: z.object({
    total: z.number().int().nonnegative(),
    by_qualification: z.object({ QUALIFIED: z.number().int().nonnegative(), NEEDS_REVIEW: z.number().int().nonnegative(), UNQUALIFIED: z.number().int().nonnegative() }),
    provenance_complete: z.number().int().nonnegative(),
    provenance_incomplete: z.number().int().nonnegative(),
  }),
  claims: z.array(z.object({
    id: z.string(),
    task_id: z.string(),
    status: z.enum(["DRAFT", "QUALIFIED", "NEEDS_REVIEW", "REJECTED"]),
    evidence_ids: z.array(z.string()),
    unresolved_evidence_ids: z.array(z.string()),
  })),
});

export type RuntimeTrace = z.infer<typeof runtimeTraceSchema>;
export type FetchLike = typeof fetch;

export interface ResearchRuntimeService {
  getTrace(runId: string): Promise<RuntimeTrace>;
}

export class HttpResearchRuntimeService implements ResearchRuntimeService {
  constructor(private readonly baseUrl: string, private readonly fetchImpl: FetchLike = fetch) {
    if (!baseUrl.trim()) throw new Error("Research Runtime base URL must not be blank.");
  }

  async getTrace(runId: string): Promise<RuntimeTrace> {
    const response = await this.fetchImpl(`${this.baseUrl.replace(/\/$/, "")}/api/v1/research-runs/${encodeURIComponent(runId)}/trace`, { headers: { accept: "application/json" } });
    if (!response.ok) throw new Error(`Research Runtime request failed with HTTP ${response.status}.`);
    return runtimeTraceSchema.parse(await response.json());
  }
}

class UnconfiguredResearchRuntimeService implements ResearchRuntimeService {
  async getTrace(): Promise<RuntimeTrace> {
    throw new Error("Research Runtime URL is not configured; local UI is using synthetic workspace data.");
  }
}

export function createResearchRuntimeService(baseUrl: string | undefined, fetchImpl: FetchLike = fetch): ResearchRuntimeService {
  return baseUrl?.trim() ? new HttpResearchRuntimeService(baseUrl, fetchImpl) : new UnconfiguredResearchRuntimeService();
}
