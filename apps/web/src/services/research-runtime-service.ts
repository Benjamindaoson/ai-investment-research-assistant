import { z } from "zod";

const runtimeTaskTraceSchema = z.object({
  id: z.string(),
  state: z.enum(["PENDING", "RUNNING", "COMPLETED", "FAILED", "UNKNOWN_EFFECT"]),
  depends_on: z.array(z.string()),
  missing_requirement_ids: z.array(z.string()),
});

const runtimeTraceSchema = z.object({
  run_id: z.string(),
  case_id: z.string(),
  state: z.enum(["CREATED", "RUNNING", "VERIFYING", "COMPLETED", "PARTIAL", "FAILED", "CANCELLED", "BLOCKED"]),
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

const evaluationCheckSchema = z.object({
  name: z.string(),
  status: z.enum(["PASS", "FAIL", "N/A", "BLOCKED"]),
  detail: z.string(),
});
const evaluationResultSchema = z.object({
  id: z.string(), case_id: z.string(), run_id: z.string().nullable().optional(), evaluator: z.string(),
  case_hash: z.string(), passed: z.boolean().nullable(), checks: z.array(evaluationCheckSchema).min(1), evaluated_at: z.string().datetime(),
});
export type EvaluationResult = z.infer<typeof evaluationResultSchema>;

const researchMandateSchema = z.object({
  decision_type: z.enum(["INVESTMENT_COMMITTEE", "DUE_DILIGENCE", "SCREENING", "MONITORING", "STRATEGIC_REVIEW"]),
  time_horizon: z.string().min(1).max(100),
  materiality: z.enum(["LOW", "MEDIUM", "HIGH"]),
  required_outputs: z.array(z.string().min(1)).min(1).max(10),
  constraints: z.array(z.string().min(1)).max(20),
});
export type ResearchMandate = z.infer<typeof researchMandateSchema>;

const runtimeResearchCaseSchema = z.object({ id: z.string(), question: z.string(), target: z.string(), mandate: researchMandateSchema, created_at: z.string().datetime().optional() });
export type RuntimeResearchCase = z.infer<typeof runtimeResearchCaseSchema>;

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
  state: z.enum(["CREATED", "RUNNING", "VERIFYING", "COMPLETED", "PARTIAL", "FAILED", "CANCELLED", "BLOCKED"]),
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
  ic_review_ids: z.array(z.string()).default([]),
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

const calculationLedgerEntrySchema = z.object({
  metric: z.string(),
  formula: z.string(),
  inputs: z.record(z.string(), z.string()),
  value: z.string().nullable(),
  unit: z.string(),
  status: z.enum(["AVAILABLE", "UNAVAILABLE"]),
  reason: z.string().nullable().optional(),
  evidence_ids: z.array(z.string()).default([]),
});
export type CalculationLedgerEntry = z.infer<typeof calculationLedgerEntrySchema>;

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
  calculation_ledger: z.array(calculationLedgerEntrySchema).default([]),
});
export type FinancialAnalysisResult = z.infer<typeof financialAnalysisResultSchema>;

const scenarioNameSchema = z.enum(["BULL", "BASE", "BEAR"]);
const scenarioAssumptionSchema = z.object({
  name: scenarioNameSchema,
  revenue_growth_pct: decimalStringSchema,
  operating_margin_pct: decimalStringSchema,
  fcf_margin_pct: decimalStringSchema,
  discount_rate_pct: decimalStringSchema,
  terminal_growth_pct: decimalStringSchema,
  net_cash: decimalStringSchema,
  shares_outstanding: decimalStringSchema,
  evidence_ids: z.record(z.string(), z.array(z.string().min(1))),
});
const scenarioValuationResultSchema = z.object({
  scenario: scenarioNameSchema,
  assumptions: scenarioAssumptionSchema,
  projected_revenue: decimalStringSchema,
  projected_operating_income: decimalStringSchema,
  free_cash_flow: decimalStringSchema,
  terminal_value: decimalStringSchema,
  equity_value: decimalStringSchema,
  value_per_share: decimalStringSchema,
});
const valuationScenariosSchema = z.object({
  id: z.string(),
  run_id: z.string(),
  case_id: z.string(),
  input_hash: z.string().length(64),
  base_revenue: decimalStringSchema,
  base_revenue_evidence_ids: z.array(z.string().min(1)),
  scenarios: z.array(scenarioValuationResultSchema).length(3),
  provenance: z.record(z.string(), z.unknown()),
});
export type ValuationScenarios = z.infer<typeof valuationScenariosSchema>;
const valuationScenarioInputSchema = z.object({
  base_revenue: decimalStringSchema,
  base_revenue_evidence_ids: z.array(z.string().min(1)).min(1),
  scenarios: z.array(scenarioAssumptionSchema).length(3),
});
export type ValuationScenarioInput = z.infer<typeof valuationScenarioInputSchema>;
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

const investmentCommitteeReviewSchema = z.object({
  id: z.string(),
  run_id: z.string(),
  thesis_id: z.string(),
  role: z.enum(["BULL", "BEAR", "FINANCIAL", "INDUSTRY", "PARTNER"]),
  reviewer: z.string(),
  position: z.enum(["SUPPORTIVE", "CHALLENGING", "MIXED", "INSUFFICIENT"]),
  recommendation: z.enum(["APPROVE", "HOLD", "REJECT", "REQUEST_RESEARCH"]),
  rationale: z.string(),
  evidence_ids: z.array(z.string()),
  created_at: z.string().datetime(),
});
const investmentCommitteeReviewInputSchema = investmentCommitteeReviewSchema.omit({ id: true, run_id: true, thesis_id: true, created_at: true });
export type InvestmentCommitteeReview = z.infer<typeof investmentCommitteeReviewSchema>;
export type InvestmentCommitteeReviewInput = z.infer<typeof investmentCommitteeReviewInputSchema>;

const decisionRecordSchema = z.object({
  id: z.string(),
  actor: z.string(),
  action: z.enum(["APPROVE_THESIS", "REJECT_THESIS", "REQUEST_RESEARCH"]),
  target_id: z.string(),
  rationale: z.string(),
  review_ids: z.array(z.string()).default([]),
  created_at: z.string().datetime(),
});
const decisionRecordInputSchema = z.object({
  actor: z.string().trim().min(1).max(200),
  action: z.enum(["APPROVE_THESIS", "REJECT_THESIS", "REQUEST_RESEARCH"]),
  target_id: z.string().min(1),
  rationale: z.string().trim().min(3).max(4000),
  review_ids: z.array(z.string().min(1)).max(100).default([]),
});
export type DecisionRecord = z.infer<typeof decisionRecordSchema>;
export type DecisionRecordInput = z.infer<typeof decisionRecordInputSchema>;

const runtimeEvidenceSchema = z.object({
  id: z.string(),
  task_id: z.string().optional(),
  requirement_id: z.string().optional(),
  stance: z.enum(["SUPPORTING", "COUNTER", "CONFLICTING"]),
  qualification: z.enum(["QUALIFIED", "NEEDS_REVIEW", "UNQUALIFIED"]),
  source_id: z.string().optional(),
  source_title: z.string().optional(),
  excerpt: z.string().optional(),
  provider: z.string().optional(),
  source_url: z.string().optional(),
  source_version: z.string().optional(),
  locator: z.string().optional(),
  content_hash: z.string().optional(),
  retrieved_at: z.string().datetime().optional(),
  provenance: z.record(z.string(), z.unknown()).optional(),
});
export type RuntimeEvidence = z.infer<typeof runtimeEvidenceSchema>;

const runtimePlanSchema = z.object({
  id: z.string(),
  case_id: z.string(),
  question: z.string(),
  planner_name: z.string(),
  planner_version: z.string(),
  input_hash: z.string().length(64),
  status: z.enum(["PROPOSED", "VALIDATED", "REJECTED"]),
  mandate: researchMandateSchema,
});
export type RuntimePlan = z.infer<typeof runtimePlanSchema>;

const runtimeEvidenceRequirementSchema = z.object({
  id: z.string(),
  description: z.string(),
  minimum_records: z.number().int().positive(),
  required_stances: z.array(z.enum(["SUPPORTING", "COUNTER", "CONFLICTING"])),
  fact_type: z.enum(["RETRIEVED_FACT", "DERIVED_FACT", "EXPLANATORY_FACT", "CONTEXT_FACT"]).optional(),
  role: z.string().optional(),
  entity: z.string().optional(),
  metric: z.string().optional(),
  period: z.string().optional(),
  criticality: z.enum(["CRITICAL", "SUPPORTING", "OPTIONAL"]).optional(),
  evidence_role: z.enum(["VALUE_SUPPORT", "COMPARISON_SUPPORT", "DERIVATION_INPUT", "EXPLANATION_SUPPORT", "CONTEXT_SUPPORT"]).nullable().optional(),
});
export type RuntimeEvidenceRequirement = z.infer<typeof runtimeEvidenceRequirementSchema>;

const runtimeTaskSchema = z.object({
  id: z.string(),
  title: z.string(),
  state: z.enum(["PENDING", "RUNNING", "COMPLETED", "FAILED", "UNKNOWN_EFFECT"]),
  purpose: z.string().optional(),
  depends_on: z.array(z.string()).optional(),
  tool_name: z.string().optional(),
  evidence_requirements: z.array(runtimeEvidenceRequirementSchema).optional(),
});
export type RuntimeTask = z.infer<typeof runtimeTaskSchema>;

const runtimeToolExecutionSchema = z.object({
  id: z.string(),
  task_id: z.string(),
  tool_name: z.string(),
  provider: z.string().optional(),
  input_hash: z.string().length(64).nullable().optional(),
  operation: z.enum(["EVIDENCE_COLLECTION", "CLAIM_VERIFICATION"]).optional(),
  verification_supported: z.boolean().nullable().optional(),
  status: z.enum(["SUCCEEDED", "FAILED", "UNKNOWN_EFFECT"]),
  attempt_key: z.string().optional(),
  result_hash: z.string(),
  evidence_count: z.number().int().nonnegative().optional(),
  qualified_evidence_count: z.number().int().nonnegative().optional(),
  review_evidence_count: z.number().int().nonnegative().optional(),
  unqualified_evidence_count: z.number().int().nonnegative().optional(),
  started_at: z.string().datetime(),
  completed_at: z.string().datetime().nullable().optional(),
  error_type: z.string().max(200).nullable().optional(),
  error_message: z.string().max(1000).nullable().optional(),
  error_hash: z.string().length(64).nullable().optional(),
  resolution: z.enum(["RETRY_AUTHORIZED", "MARKED_FAILED"]).nullable().optional(),
});
export type RuntimeToolExecution = z.infer<typeof runtimeToolExecutionSchema>;

const runtimeClaimSchema = z.object({
  id: z.string(),
  task_id: z.string().optional(),
  statement: z.string().optional(),
  status: z.enum(["DRAFT", "QUALIFIED", "NEEDS_REVIEW", "REJECTED"]),
  confidence: z.number().min(0).max(1).optional(),
  evidence_ids: z.array(z.string()),
});
export type RuntimeClaim = z.infer<typeof runtimeClaimSchema>;

const runtimeRunSchema = z.object({
  id: z.string(),
  case_id: z.string(),
  plan: runtimePlanSchema.optional(),
  state: z.enum(["CREATED", "RUNNING", "VERIFYING", "COMPLETED", "PARTIAL", "FAILED", "CANCELLED", "BLOCKED"]),
  tasks: z.array(runtimeTaskSchema),
  tool_executions: z.array(runtimeToolExecutionSchema).default([]),
  evidence: z.array(runtimeEvidenceSchema),
  claims: z.array(runtimeClaimSchema),
  thesis: z.object({ id: z.string(), statement: z.string(), bull: z.string(), base: z.string(), bear: z.string(), claim_ids: z.array(z.string()), review_status: z.enum(["PENDING_REVIEW", "APPROVED", "NEEDS_REVIEW"]), provenance: z.record(z.string(), z.unknown()).optional() }).nullable(),
  memo: runtimeMemoSchema.nullable(),
  financial_analysis: financialAnalysisResultSchema.nullable().default(null),
  valuation_scenarios: valuationScenariosSchema.nullable().optional(),
  red_team_reviews: z.array(redTeamReviewSchema).default([]),
  ic_reviews: z.array(investmentCommitteeReviewSchema).default([]),
  decisions: z.array(decisionRecordSchema).default([]),
  created_at: z.string().datetime().optional(),
  updated_at: z.string().datetime().optional(),
  completed_at: z.string().datetime().nullable().optional(),
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
  getCases(): Promise<RuntimeResearchCase[]>;
  createCaseRun(caseId: string): Promise<RuntimeCaseResult>;
  getRun(runId: string): Promise<RuntimeRun>;
  getCaseRuns(caseId: string): Promise<RuntimeRun[]>;
  getEvaluation(runId: string): Promise<EvaluationResult | null>;
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
  getValuationScenarios(runId: string): Promise<ValuationScenarios>;
  analyzeValuationScenarios(runId: string, input: ValuationScenarioInput): Promise<ValuationScenarios>;
  createRedTeamReview(runId: string, input: RedTeamReviewInput): Promise<RuntimeRun>;
  getRedTeamReviews(runId: string): Promise<RedTeamReview[]>;
  createInvestmentCommitteeReview(runId: string, input: InvestmentCommitteeReviewInput): Promise<RuntimeRun>;
  getInvestmentCommitteeReviews(runId: string): Promise<InvestmentCommitteeReview[]>;
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

  async getCases(): Promise<RuntimeResearchCase[]> {
    return z.array(runtimeResearchCaseSchema).parse(await this.requestJson("/api/v1/research-cases", { headers: { accept: "application/json" } }));
  }

  async createCaseRun(caseId: string): Promise<RuntimeCaseResult> {
    return runtimeCaseResultSchema.parse(await this.requestJson(`/api/v1/research-cases/${encodeURIComponent(caseId)}/runs`, {
      method: "POST",
      headers: { accept: "application/json", "content-type": "application/json" },
      body: JSON.stringify({}),
    }));
  }

  async getRun(runId: string): Promise<RuntimeRun> {
    return runtimeRunSchema.parse(await this.requestJson(`/api/v1/research-runs/${encodeURIComponent(runId)}`, { headers: { accept: "application/json" } }));
  }

  async getCaseRuns(caseId: string): Promise<RuntimeRun[]> {
    return z.array(runtimeRunSchema).parse(await this.requestJson(`/api/v1/research-cases/${encodeURIComponent(caseId)}/runs`, { headers: { accept: "application/json" } }));
  }

  async getEvaluation(runId: string): Promise<EvaluationResult | null> {
    try {
      return evaluationResultSchema.parse(await this.requestJson(`/api/v1/research-runs/${encodeURIComponent(runId)}/evaluation`, { headers: { accept: "application/json" } }));
    } catch (error) {
      if (error instanceof Error && error.message === "Research Runtime request failed with HTTP 404.") return null;
      throw error;
    }
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

  async getValuationScenarios(runId: string): Promise<ValuationScenarios> {
    return valuationScenariosSchema.parse(await this.requestJson("/api/v1/research-runs/" + encodeURIComponent(runId) + "/valuation-scenarios", {
      headers: { accept: "application/json" },
    }));
  }

  async analyzeValuationScenarios(runId: string, input: ValuationScenarioInput): Promise<ValuationScenarios> {
    const body = valuationScenarioInputSchema.parse(input);
    return valuationScenariosSchema.parse(await this.requestJson("/api/v1/research-runs/" + encodeURIComponent(runId) + "/valuation-scenarios", {
      method: "POST",
      headers: { accept: "application/json", "content-type": "application/json" },
      body: JSON.stringify(body),
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

  async createInvestmentCommitteeReview(runId: string, input: InvestmentCommitteeReviewInput): Promise<RuntimeRun> {
    const body = investmentCommitteeReviewInputSchema.parse(input);
    return runtimeRunSchema.parse(await this.requestJson(`/api/v1/research-runs/${encodeURIComponent(runId)}/ic-reviews`, {
      method: "POST",
      headers: { accept: "application/json", "content-type": "application/json" },
      body: JSON.stringify(body),
    }));
  }

  async getInvestmentCommitteeReviews(runId: string): Promise<InvestmentCommitteeReview[]> {
    return z.array(investmentCommitteeReviewSchema).parse(await this.requestJson(`/api/v1/research-runs/${encodeURIComponent(runId)}/ic-reviews`, { headers: { accept: "application/json" } }));
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
  async getCases(): Promise<RuntimeResearchCase[]> { return this.unavailable(); }
  async createCaseRun(): Promise<RuntimeCaseResult> { return this.unavailable(); }
  async getEvaluation(): Promise<EvaluationResult | null> { return this.unavailable(); }
  async getRun(): Promise<RuntimeRun> { return this.unavailable(); }
  async getCaseRuns(): Promise<RuntimeRun[]> { return this.unavailable(); }
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
  async getValuationScenarios(): Promise<ValuationScenarios> { return this.unavailable(); }
  async analyzeValuationScenarios(): Promise<ValuationScenarios> { return this.unavailable(); }
  async createRedTeamReview(): Promise<RuntimeRun> { return this.unavailable(); }
  async getRedTeamReviews(): Promise<RedTeamReview[]> { return this.unavailable(); }
  async createInvestmentCommitteeReview(): Promise<RuntimeRun> { return this.unavailable(); }
  async getInvestmentCommitteeReviews(): Promise<InvestmentCommitteeReview[]> { return this.unavailable(); }
  async recordDecision(): Promise<RuntimeRun> { return this.unavailable(); }
}

export function createResearchRuntimeService(baseUrl: string | undefined, fetchImpl: FetchLike = fetch.bind(globalThis)): ResearchRuntimeService {
  return baseUrl?.trim() ? new HttpResearchRuntimeService(baseUrl, fetchImpl) : new UnconfiguredResearchRuntimeService();
}
