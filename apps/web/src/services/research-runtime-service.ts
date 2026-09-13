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

const researchMandateSchema = z.object({
  decision_type: z.enum(["INVESTMENT_COMMITTEE", "DUE_DILIGENCE", "SCREENING", "MONITORING", "STRATEGIC_REVIEW"]),
  time_horizon: z.string().min(1).max(100),
  materiality: z.enum(["LOW", "MEDIUM", "HIGH"]),
  required_outputs: z.array(z.string().min(1)).min(1).max(10),
  constraints: z.array(z.string().min(1)).max(20),
});
export type ResearchMandate = z.infer<typeof researchMandateSchema>;

const runtimeCaseInputSchema = z.object({
  question: z.string().min(3),
  target: z.string().min(1),
  mandate: researchMandateSchema.optional(),
});
export type RuntimeCaseInput = z.infer<typeof runtimeCaseInputSchema>;

const runtimeCaseResultSchema = z.object({ case_id: z.string(), run_id: z.string() });
export type RuntimeCaseResult = z.infer<typeof runtimeCaseResultSchema>;

const runtimeRunControlSchema = z.object({
  id: z.string(),
  case_id: z.string(),
  state: z.enum(["CREATED", "RUNNING", "VERIFYING", "COMPLETED", "PARTIAL", "FAILED", "CANCELLED"]),
});
export type RuntimeRunControl = z.infer<typeof runtimeRunControlSchema>;

const runtimeMemoSectionSchema = z.object({
  section_key: z.enum(["thesis", "evidence", "risks", "scenarios", "decision"]),
  title: z.string(),
  body: z.string().min(3),
  claim_ids: z.array(z.string()),
  evidence_ids: z.array(z.string()),
  unresolved_requirement_ids: z.array(z.string()),
});

const runtimeMemoSchema = z.object({
  id: z.string(),
  run_id: z.string(),
  case_id: z.string(),
  title: z.string(),
  status: z.enum(["DRAFT", "READY_FOR_REVIEW", "APPROVED"]),
  executive_summary: z.string(),
  thesis_id: z.string(),
  claim_ids: z.array(z.string()),
  evidence_ids: z.array(z.string()),
  counter_evidence_ids: z.array(z.string()),
  unresolved_requirement_ids: z.array(z.string()),
  sections: z.array(runtimeMemoSectionSchema).default([]),
  provenance: z.record(z.string(), z.unknown()),
  generated_at: z.string().datetime(),
});
export type RuntimeMemo = z.infer<typeof runtimeMemoSchema>;

const decimalStringSchema = z.string().regex(/^-?\d+(\.\d+)?$/, "Expected a decimal string.");
const financialSnapshotSchema = z.object({
  period: z.string().min(1),
  revenue: z.string().regex(/^\d+(\.\d+)?$/, "Expected a non-negative decimal string."),
  prior_revenue: z.string().regex(/^\d+(\.\d+)?$/).nullable().optional(),
  gross_profit: decimalStringSchema.nullable().optional(),
  operating_income: decimalStringSchema.nullable().optional(),
  operating_cash_flow: decimalStringSchema.nullable().optional(),
  capex: z.string().regex(/^\d+(\.\d+)?$/).nullable().optional(),
  cash: z.string().regex(/^\d+(\.\d+)?$/).nullable().optional(),
  debt: z.string().regex(/^\d+(\.\d+)?$/).nullable().optional(),
});
export type FinancialSnapshotInput = z.infer<typeof financialSnapshotSchema>;

const financialAnalysisResultSchema = z.object({
  period: z.string(),
  snapshot: financialSnapshotSchema,
  input_hash: z.string().length(64),
  revenue_growth_pct: z.string().nullable(),
  gross_margin_pct: z.string().nullable(),
  operating_margin_pct: z.string().nullable(),
  free_cash_flow: z.string().nullable(),
  fcf_margin_pct: z.string().nullable(),
  net_cash: z.string().nullable(),
  unavailable_metrics: z.array(z.string()),
  evidence_ids: z.record(z.string(), z.array(z.string())).default({}),
});
export type FinancialAnalysisResult = z.infer<typeof financialAnalysisResultSchema>;
const evidenceLinkedFinancialAnalysisInputSchema = z.object({
  snapshot: financialSnapshotSchema,
  evidence_ids: z.record(z.string(), z.array(z.string().min(1)).min(1)),
});
export type EvidenceLinkedFinancialAnalysisInput = z.infer<typeof evidenceLinkedFinancialAnalysisInputSchema>;

const redTeamReviewSchema = z.object({
  id: z.string(),
  run_id: z.string(),
  thesis_id: z.string(),
  reviewer: z.string(),
  challenge: z.string(),
  evidence_ids: z.array(z.string()),
  outcome: z.enum(["OPEN", "SUPPORTED", "REJECTED", "REQUIRES_RESEARCH"]),
  rationale: z.string(),
  created_at: z.string().datetime(),
});
const redTeamReviewInputSchema = z.object({
  reviewer: z.string().trim().min(1).max(200),
  challenge: z.string().trim().min(1),
  evidence_ids: z.array(z.string().min(1)).min(1),
  outcome: z.enum(["OPEN", "SUPPORTED", "REJECTED", "REQUIRES_RESEARCH"]),
  rationale: z.string().trim().min(1),
});
export type RedTeamReview = z.infer<typeof redTeamReviewSchema>;
export type RedTeamReviewInput = z.infer<typeof redTeamReviewInputSchema>;

const decisionRecordSchema = z.object({
  id: z.string(),
  actor: z.string(),
  action: z.enum(["APPROVE_THESIS", "REJECT_THESIS", "REQUEST_RESEARCH"]),
  target_id: z.string(),
  rationale: z.string(),
  created_at: z.string().datetime(),
});
const decisionRecordInputSchema = z.object({
  actor: z.string().trim().min(1).max(200),
  action: z.enum(["APPROVE_THESIS", "REJECT_THESIS", "REQUEST_RESEARCH"]),
  target_id: z.string().min(1),
  rationale: z.string().trim().min(3).max(4000),
});
export type DecisionRecord = z.infer<typeof decisionRecordSchema>;
export type DecisionRecordInput = z.infer<typeof decisionRecordInputSchema>;

const runtimeRunSchema = z.object({
  id: z.string(),
  case_id: z.string(),
  state: z.enum(["CREATED", "RUNNING", "VERIFYING", "COMPLETED", "PARTIAL", "FAILED", "CANCELLED"]),
  tasks: z.array(z.object({ id: z.string(), title: z.string(), state: z.enum(["PENDING", "RUNNING", "COMPLETED", "FAILED"]) })),
  evidence: z.array(z.object({ id: z.string(), source_title: z.string().optional(), stance: z.enum(["SUPPORTING", "COUNTER", "CONFLICTING"]), qualification: z.enum(["QUALIFIED", "NEEDS_REVIEW", "UNQUALIFIED"]) })),
  claims: z.array(z.object({ id: z.string(), status: z.enum(["DRAFT", "QUALIFIED", "NEEDS_REVIEW", "REJECTED"]), evidence_ids: z.array(z.string()) })),
  thesis: z.object({ id: z.string(), statement: z.string(), bull: z.string(), base: z.string(), bear: z.string(), claim_ids: z.array(z.string()), review_status: z.enum(["PENDING_REVIEW", "APPROVED", "NEEDS_REVIEW"]) }).nullable(),
  memo: runtimeMemoSchema.nullable(),
  financial_analysis: financialAnalysisResultSchema.nullable().default(null),
  red_team_reviews: z.array(redTeamReviewSchema).default([]),
  decisions: z.array(decisionRecordSchema).default([]),
}).passthrough();
export type RuntimeRun = z.infer<typeof runtimeRunSchema>;

const investmentMemorySchema = z.object({
  id: z.string(),
  target: z.string(),
  case_ids: z.array(z.string()),
  run_ids: z.array(z.string()),
  memo_ids: z.array(z.string()),
  thesis_ids: z.array(z.string()),
  latest_run_id: z.string(),
  latest_thesis_id: z.string(),
  previous_thesis_id: z.string().nullable(),
  latest_thesis_delta: z.object({
    previous_thesis_id: z.string(),
    current_thesis_id: z.string(),
    qualified_evidence_delta: z.number().int(),
    counter_conflicting_evidence_delta: z.number().int(),
    unresolved_requirement_delta: z.number().int(),
    summary: z.string(),
    observed_at: z.string().datetime(),
  }).nullable().default(null),
  unresolved_requirement_ids: z.array(z.string()),
  decision_ids: z.array(z.string()),
  updated_at: z.string().datetime(),
});
export type InvestmentMemory = z.infer<typeof investmentMemorySchema>;

export interface ResearchRuntimeService {
  createCase(input: RuntimeCaseInput): Promise<RuntimeCaseResult>;
  getRun(runId: string): Promise<RuntimeRun>;
  executeRun(runId: string): Promise<RuntimeRun>;
  replanRun(runId: string): Promise<RuntimeRun>;
  getTrace(runId: string): Promise<RuntimeTrace>;
  cancelRun(runId: string, reason: string): Promise<RuntimeRunControl>;
  getMemo(runId: string): Promise<RuntimeMemo>;
  getMemory(target: string): Promise<InvestmentMemory>;
  getMemoryForRun(runId: string): Promise<InvestmentMemory>;
  analyzeFinancials(snapshot: FinancialSnapshotInput): Promise<FinancialAnalysisResult>;
  analyzeFinancialsForRun(runId: string, input: EvidenceLinkedFinancialAnalysisInput): Promise<FinancialAnalysisResult>;
  getFinancialAnalysisForRun(runId: string): Promise<FinancialAnalysisResult>;
  createRedTeamReview(runId: string, input: RedTeamReviewInput): Promise<RuntimeRun>;
  getRedTeamReviews(runId: string): Promise<RedTeamReview[]>;
  recordDecision(runId: string, input: DecisionRecordInput): Promise<RuntimeRun>;
}

export class HttpResearchRuntimeService implements ResearchRuntimeService {
  constructor(private readonly baseUrl: string, private readonly fetchImpl: FetchLike = fetch) {
    if (!baseUrl.trim()) throw new Error("Research Runtime base URL must not be blank.");
  }

  private async requestJson(path: string, init?: RequestInit): Promise<unknown> {
    const response = await this.fetchImpl(`${this.baseUrl.replace(/\/$/, "")}${path}`, init);
    if (!response.ok) throw new Error(`Research Runtime request failed with HTTP ${response.status}.`);
    return response.json();
  }

  async createCase(input: RuntimeCaseInput): Promise<RuntimeCaseResult> {
    const body = runtimeCaseInputSchema.parse(input);
    return runtimeCaseResultSchema.parse(await this.requestJson("/api/v1/research-cases", {
      method: "POST",
      headers: { accept: "application/json", "content-type": "application/json" },
      body: JSON.stringify(body),
    }));
  }

  async getRun(runId: string): Promise<RuntimeRun> {
    return runtimeRunSchema.parse(await this.requestJson(`/api/v1/research-runs/${encodeURIComponent(runId)}`, { headers: { accept: "application/json" } }));
  }

  async executeRun(runId: string): Promise<RuntimeRun> {
    return runtimeRunSchema.parse(await this.requestJson(`/api/v1/research-runs/${encodeURIComponent(runId)}/execute`, {
      method: "POST",
      headers: { accept: "application/json", "content-type": "application/json" },
      body: JSON.stringify({}),
    }));
  }

  async replanRun(runId: string): Promise<RuntimeRun> {
    return runtimeRunSchema.parse(await this.requestJson("/api/v1/research-runs/" + encodeURIComponent(runId) + "/replan", {
      method: "POST",
      headers: { accept: "application/json", "content-type": "application/json" },
      body: JSON.stringify({}),
    }));
  }

  async getTrace(runId: string): Promise<RuntimeTrace> {
    return runtimeTraceSchema.parse(await this.requestJson(`/api/v1/research-runs/${encodeURIComponent(runId)}/trace`, { headers: { accept: "application/json" } }));
  }

  async cancelRun(runId: string, reason: string): Promise<RuntimeRunControl> {
    if (reason.trim().length < 3) throw new Error("Cancellation reason must be at least 3 characters.");
    return runtimeRunControlSchema.parse(await this.requestJson(`/api/v1/research-runs/${encodeURIComponent(runId)}/cancel`, {
      method: "POST",
      headers: { accept: "application/json", "content-type": "application/json" },
      body: JSON.stringify({ reason }),
    }));
  }

  async getMemo(runId: string): Promise<RuntimeMemo> {
    return runtimeMemoSchema.parse(await this.requestJson(`/api/v1/research-runs/${encodeURIComponent(runId)}/memo`, { headers: { accept: "application/json" } }));
  }

  async getMemory(target: string): Promise<InvestmentMemory> {
    return investmentMemorySchema.parse(await this.requestJson(`/api/v1/investment-memory/${encodeURIComponent(target)}`, { headers: { accept: "application/json" } }));
  }

  async getMemoryForRun(runId: string): Promise<InvestmentMemory> {
    return investmentMemorySchema.parse(await this.requestJson(`/api/v1/research-runs/${encodeURIComponent(runId)}/memory`, { headers: { accept: "application/json" } }));
  }

  async analyzeFinancials(snapshot: FinancialSnapshotInput): Promise<FinancialAnalysisResult> {
    const input = financialSnapshotSchema.parse(snapshot);
    return financialAnalysisResultSchema.parse(await this.requestJson("/api/v1/financial-analysis", {
      method: "POST",
      headers: { accept: "application/json", "content-type": "application/json" },
      body: JSON.stringify(input),
    }));
  }

  async analyzeFinancialsForRun(runId: string, input: EvidenceLinkedFinancialAnalysisInput): Promise<FinancialAnalysisResult> {
    const body = evidenceLinkedFinancialAnalysisInputSchema.parse(input);
    return financialAnalysisResultSchema.parse(await this.requestJson("/api/v1/research-runs/" + encodeURIComponent(runId) + "/financial-analysis", {
      method: "POST",
      headers: { accept: "application/json", "content-type": "application/json" },
      body: JSON.stringify(body),
    }));
  }

  async getFinancialAnalysisForRun(runId: string): Promise<FinancialAnalysisResult> {
    return financialAnalysisResultSchema.parse(await this.requestJson("/api/v1/research-runs/" + encodeURIComponent(runId) + "/financial-analysis", {
      headers: { accept: "application/json" },
    }));
  }

  async createRedTeamReview(runId: string, input: RedTeamReviewInput): Promise<RuntimeRun> {
    const body = redTeamReviewInputSchema.parse(input);
    return runtimeRunSchema.parse(await this.requestJson("/api/v1/research-runs/" + encodeURIComponent(runId) + "/red-team-reviews", {
      method: "POST",
      headers: { accept: "application/json", "content-type": "application/json" },
      body: JSON.stringify(body),
    }));
  }

  async getRedTeamReviews(runId: string): Promise<RedTeamReview[]> {
    return z.array(redTeamReviewSchema).parse(await this.requestJson("/api/v1/research-runs/" + encodeURIComponent(runId) + "/red-team-reviews", { headers: { accept: "application/json" } }));
  }

  async recordDecision(runId: string, input: DecisionRecordInput): Promise<RuntimeRun> {
    const body = decisionRecordInputSchema.parse(input);
    return runtimeRunSchema.parse(await this.requestJson("/api/v1/research-runs/" + encodeURIComponent(runId) + "/decisions", {
      method: "POST",
      headers: { accept: "application/json", "content-type": "application/json" },
      body: JSON.stringify(body),
    }));
  }
}

class UnconfiguredResearchRuntimeService implements ResearchRuntimeService {
  private unavailable(): never {
    throw new Error("Research Runtime URL is not configured; local UI is using synthetic workspace data.");
  }

  async createCase(): Promise<RuntimeCaseResult> { return this.unavailable(); }
  async getRun(): Promise<RuntimeRun> { return this.unavailable(); }
  async executeRun(): Promise<RuntimeRun> { return this.unavailable(); }
  async replanRun(): Promise<RuntimeRun> { return this.unavailable(); }
  async getTrace(): Promise<RuntimeTrace> { return this.unavailable(); }
  async cancelRun(): Promise<RuntimeRunControl> { return this.unavailable(); }
  async getMemo(): Promise<RuntimeMemo> { return this.unavailable(); }
  async getMemory(): Promise<InvestmentMemory> { return this.unavailable(); }
  async getMemoryForRun(): Promise<InvestmentMemory> { return this.unavailable(); }
  async analyzeFinancials(): Promise<FinancialAnalysisResult> { return this.unavailable(); }
  async analyzeFinancialsForRun(): Promise<FinancialAnalysisResult> { return this.unavailable(); }
  async getFinancialAnalysisForRun(): Promise<FinancialAnalysisResult> { return this.unavailable(); }
  async createRedTeamReview(): Promise<RuntimeRun> { return this.unavailable(); }
  async getRedTeamReviews(): Promise<RedTeamReview[]> { return this.unavailable(); }
  async recordDecision(): Promise<RuntimeRun> { return this.unavailable(); }
}

export function createResearchRuntimeService(baseUrl: string | undefined, fetchImpl: FetchLike = fetch.bind(globalThis)): ResearchRuntimeService {
  return baseUrl?.trim() ? new HttpResearchRuntimeService(baseUrl, fetchImpl) : new UnconfiguredResearchRuntimeService();
}
