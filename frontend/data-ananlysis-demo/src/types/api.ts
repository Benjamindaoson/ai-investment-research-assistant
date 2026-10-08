// ─── Core Types ────────────────────────────────────────────────────────────────

export type AnalysisStatus =
  | "preparing" | "running" | "clarifying" | "partial" | "done"
  | "failed" | "cancelled" | "insufficient";

export type PhaseStatus = "waiting" | "running" | "done";

// ─── Analysis Types ────────────────────────────────────────────────────────────

export interface AnalysisPhase {
  id: string;
  label: string;
  status: PhaseStatus;
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

export interface FollowUpEntry {
  question: string;
  findings: FindingBlock[];
  timestamp: string;
}

export interface Analysis {
  id: string;
  question: string;
  status: AnalysisStatus;
  createdAt: string;
  updatedAt: string;
  phases: AnalysisPhase[];
  currentPhaseIndex: number;
  findings: FindingBlock[];
  insights: string[];
  followUps: FollowUpEntry[];
  failureReason?: string;
  clarificationQuestion?: string;
  reportGenerated?: boolean;
  summary?: string;
  state?: string;
  plan?: {
    steps: Array<{ id: string; description: string; status: string }>;
    message?: string;
  };
  hypotheses?: Array<{ id: string; text: string; status: string }>;
  observations?: Array<{ id: string; text: string }>;
  contributions?: Array<{ dimension: string; value: number; label: string }>;
  events?: Array<{ id: string; type: string; data: unknown }>;
  claims?: Array<{ id: string; text: string; confidence: number }>;
  evidence?: Array<{
    evidence_id: string;
    type: string;
    description: string;
    data: unknown;
    source: string;
  }>;
}

// ─── API Response Types ────────────────────────────────────────────────────────

export interface HomeData {
  dataset: DatasetStatus;
  recent_analyses: Analysis[];
  suggestions: string[];
  metrics: MetricDefinition[];
}

export interface DatasetStatus {
  snapshot_id: string;
  available: boolean;
  measured_row_count?: number;
  measured_business_date_min?: string;
  measured_business_date_max?: string;
  status?: string;
  warning?: string;
}

export interface DataStatus {
  dataset: DatasetStatus;
  dimensions: Array<{ id: string; label: string }>;
  metrics: MetricDefinition[];
}

export interface MetricDefinition {
  id: string;
  label: string;
  unit?: string;
  expression?: string;
  availability?: string;
  description?: string;
}

export interface AnalysisTaskList {
  items: Analysis[];
}

export interface CreateTaskRequest {
  question: string;
  user_context?: Record<string, unknown>;
}

export interface CreateTaskResponse extends Analysis {}

export interface InvestigationData {
  hypotheses: Array<{ id: string; text: string; status: string }>;
  observations: Array<{ id: string; text: string }>;
  contributions: Array<{ dimension: string; value: number; label: string }>;
  events: Array<{ id: string; type: string; data: unknown }>;
}

export interface ClaimsData {
  items: Array<{ id: string; text: string; confidence: number }>;
}

export interface EvidenceData {
  items: Array<{
    evidence_id: string;
    type: string;
    description: string;
    data: unknown;
    source: string;
  }>;
}

export interface PlanData {
  steps: Array<{ id: string; description: string; status: string }>;
  message?: string;
}

// ─── Evaluation Types ──────────────────────────────────────────────────────────

export interface EvaluationMetrics {
  name: string;
  status: "MEASURED" | "NOT_MEASURED";
  value?: number;
}

export interface EvaluationData {
  suite_version: string;
  case_count: number;
  status: "MEASURED" | "CASES_LOADED_NOT_RUN";
  latest_run: EvaluationRun | null;
  metrics: EvaluationMetrics[];
  note: string;
}

export interface EvaluationRun {
  suite_version: string;
  run_id: string;
  completed_at: string;
  passed: number;
  failed: number;
  results: EvaluationResult[];
  metrics: Array<{ name: string; status: string; value: number }>;
}

export interface EvaluationResult {
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

// ─── API Error ─────────────────────────────────────────────────────────────────

export interface ApiError {
  message: string;
  status?: number;
}
