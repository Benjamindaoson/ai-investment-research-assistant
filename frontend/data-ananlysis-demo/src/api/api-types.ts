/**
 * API Type Definitions - 100% aligned with backend contracts
 */

// ─── Health ──────────────────────────────────────────────────────────────────

export interface HealthStatus {
  status: string;
  product: string;
  data_available: boolean;
}

// ─── Home ──────────────────────────────────────────────────────────────────

export interface DatasetInfo {
  snapshot_id: string;
  status: string;
  available: boolean;
  measured_row_count?: number;
  measured_business_date_min?: string;
  measured_business_date_max?: string;
  warning?: string;
}

export interface MetricDefinition {
  id: string;
  label: string;
  unit?: string;
  expression?: string;
  availability?: string;
  description?: string;
}

export interface HomeData {
  dataset: DatasetInfo;
  recent_analyses: AnalysisSummary[];
  suggestions: string[];
  metrics: MetricDefinition[];
}

// ─── Data Status ────────────────────────────────────────────────────────────

export interface DimensionInfo {
  id: string;
  label: string;
}

export interface DataStatus {
  dataset: DatasetInfo;
  dimensions: DimensionInfo[];
  metrics: MetricDefinition[];
}

// ─── Analysis Task ──────────────────────────────────────────────────────────

export type TaskState =
  | "CREATED"
  | "RUNNING"
  | "PARTIAL"
  | "COMPLETED"
  | "FAILED"
  | "CANCELLED";

export interface PhaseInfo {
  id: string;
  label: string;
  status: "waiting" | "running" | "done";
}

export interface FindingBlock {
  type: "text" | "chart-trend" | "chart-contrib" | "chart-breakdown" | "table";
  id: string;
  title?: string;
  content?: string;
  data?: unknown[];
  columns?: string[];
  rows?: string[][];
  source?: string;
  sourceDetail?: string;
}

export interface AnalysisSummary {
  id: string;
  question: string;
  status: string;
  state?: TaskState;
  createdAt: string;
  updatedAt: string;
  phases?: PhaseInfo[];
  currentPhaseIndex?: number;
  summary?: string;
  clarificationQuestion?: string;
  clarification_response?: string;
  user_context?: Record<string, unknown>;
}

export interface TaskDetail extends AnalysisSummary {
  plan?: PlanData;
  hypotheses?: Hypothesis[];
  observations?: Observation[];
  contributions?: Contribution[];
  events?: TaskEvent[];
  claims?: Claim[];
  evidence?: Evidence[];
  artifacts?: Artifact[];
  findings?: FindingBlock[];
  insights?: string[];
  followUps?: FollowUp[];
  limitations?: string[];
  feedback?: Feedback[];
  replay?: {
    status: string;
    source_checkpoint?: string;
    replayed_at?: string;
  };
  resolved_context?: ResolvedContext;
  checkpoint?: unknown;
}

export interface ResolvedContext {
  context_version: string;
  metrics?: Array<{ id: string; label: string }>;
  primary_period?: { start: string; end: string };
  compare_period?: { start: string; end: string };
  dimensions?: string[];
  filters?: Record<string, string>;
}

export interface PlanData {
  steps: Array<{
    id: string;
    description: string;
    status: "pending" | "running" | "completed" | "skipped";
  }>;
  message?: string;
}

export interface Hypothesis {
  id: string;
  text: string;
  status: "proposed" | "testing" | "supported" | "rejected" | "inconclusive";
}

export interface Observation {
  id: string;
  text: string;
  hypothesis_id?: string;
}

export interface Contribution {
  dimension: string;
  value: number;
  label: string;
}

export interface TaskEvent {
  id: string;
  event_type: string;
  timestamp: string;
  data?: unknown;
}

export interface Claim {
  id: string;
  text: string;
  type: "FACT" | "INFERENCE" | "QUALIFIED" | "RECOMMENDATION";
  confidence: number;
  status: "SUPPORTED" | "QUALIFIED" | "REJECTED" | "INCONCLUSIVE";
  observation_ids?: string[];
  evidence_ids?: string[];
}

export interface Evidence {
  evidence_id: string;
  type: "observation" | "query" | "computation" | "external";
  description: string;
  data?: unknown;
  source: string;
  query_id?: string;
  computation_id?: string;
  validation?: ValidationResult;
}

export interface ValidationResult {
  metric: boolean;
  time: boolean;
  join?: boolean;
  reconciliation?: boolean;
  freshness?: boolean;
}

export interface Artifact {
  filename: string;
  type: "report" | "chart" | "data";
  created_at: string;
}

export interface FollowUp {
  question: string;
  timestamp: string;
  answer?: string;
}

export interface Feedback {
  rating: number;
  comment: string;
  created_at: string;
}

// ─── Create Task ───────────────────────────────────────────────────────────

export interface CreateTaskRequest {
  question: string;
  user_context?: Record<string, unknown>;
}

export interface CreateTaskResponse extends TaskDetail {}

// ─── Investigation ────────────────────────────────────────────────────────

export interface InvestigationData {
  hypotheses: Hypothesis[];
  observations: Observation[];
  contributions: Contribution[];
  events: TaskEvent[];
}

// ─── Claims ────────────────────────────────────────────────────────────────

export interface ClaimsData {
  items: Claim[];
}

// ─── Evidence ─────────────────────────────────────────────────────────────

export interface EvidenceData {
  items: Evidence[];
}

// ─── Artifacts ─────────────────────────────────────────────────────────────

export interface ArtifactData {
  items: Artifact[];
}

// ─── Evaluation ────────────────────────────────────────────────────────────

export interface EvaluationMetrics {
  name: string;
  status: "MEASURED" | "NOT_MEASURED";
  value?: number;
}

export interface EvaluationCaseResult {
  case_id: string;
  passed: boolean;
  state: string;
  checks: {
    semantic: boolean;
    period?: boolean;
    outcome: boolean;
    evidence: boolean;
  };
  details?: string;
}

export interface EvaluationRun {
  suite_version: string;
  run_id: string;
  completed_at: string;
  passed: number;
  failed: number;
  results: EvaluationCaseResult[];
  metrics: Array<{ name: string; status: string; value: number }>;
}

export interface EvaluationData {
  suite_version: string;
  case_count: number;
  status: "MEASURED" | "CASES_LOADED_NOT_RUN";
  latest_run: EvaluationRun | null;
  metrics: EvaluationMetrics[];
  note: string;
}

// ─── Semantic ──────────────────────────────────────────────────────────────

export interface SemanticData {
  status: "unavailable" | "loaded";
  version?: string;
  metrics?: MetricDefinition[];
  dimensions?: DimensionInfo[];
}

// ─── Settings ─────────────────────────────────────────────────────────────

export interface SettingsData {
  provider: string;
  dataset_version: string;
  semantic_version: string;
  analysis_budget: {
    max_queries: number;
    max_tool_calls: number;
    max_investigation_depth: number;
    max_result_rows: number;
  };
  credential_configured: boolean;
}

// ─── Task List ────────────────────────────────────────────────────────────

export interface AnalysisTaskList {
  items: AnalysisSummary[];
}
