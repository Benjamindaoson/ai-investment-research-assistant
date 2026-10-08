/**
 * API Client for Enterprise Intelligence Workspace
 * 100%对接后端API，无mock数据
 */

import type {
  HomeData,
  DataStatus,
  AnalysisTaskList,
  CreateTaskRequest,
  CreateTaskResponse,
  InvestigationData,
  ClaimsData,
  EvidenceData,
  PlanData,
  EvaluationData,
  EvaluationRun,
  HealthStatus,
  TaskDetail,
  ArtifactData,
  SemanticData,
  SettingsData,
} from "./api-types";

// API Base
const API_BASE = "/api/v1";

class ApiError extends Error {
  constructor(
    message: string,
    public status?: number,
    public detail?: string
  ) {
    super(message);
    this.name = "ApiError";
  }
}

async function request<T>(
  path: string,
  options: RequestInit = {}
): Promise<T> {
  const url = `${API_BASE}${path}`;
  const response = await fetch(url, {
    ...options,
    headers: {
      "Content-Type": "application/json",
      ...options.headers,
    },
  });

  if (!response.ok) {
    let detail: string | undefined;
    try {
      const data = await response.json();
      detail = data.detail;
    } catch {
      // ignore
    }
    throw new ApiError(
      detail || `HTTP ${response.status}`,
      response.status,
      detail
    );
  }

  return response.json();
}

// Health & Status
export const health = {
  check: () => request<HealthStatus>("/health"),
};

// Home
export const homeApi = {
  get: () => request<HomeData>("/home"),
};

// Data
export const dataApi = {
  status: () => request<DataStatus>("/data/status"),
};

// Analysis Tasks
export const analysisApi = {
  list: () => request<AnalysisTaskList>("/analysis-tasks"),

  get: (id: string) => request<TaskDetail>(`/analysis-tasks/${id}`),

  create: (data: CreateTaskRequest) =>
    request<CreateTaskResponse>("/analysis-tasks", {
      method: "POST",
      body: JSON.stringify(data),
    }),

  cancel: (id: string) =>
    request<TaskDetail>(`/analysis-tasks/${id}/cancel`, {
      method: "POST",
    }),

  plan: (id: string) => request<PlanData>(`/analysis-tasks/${id}/plan`),

  investigation: (id: string) =>
    request<InvestigationData>(`/analysis-tasks/${id}/investigation`),

  claims: (id: string) => request<ClaimsData>(`/analysis-tasks/${id}/claims`),

  evidence: (id: string) => request<EvidenceData>(`/analysis-tasks/${id}/evidence`),

  evidenceDetail: (id: string, evidenceId: string) =>
    request<EvidenceData["items"][0]>(
      `/analysis-tasks/${id}/evidence/${evidenceId}`
    ),

  artifacts: (id: string) => request<ArtifactData>(`/analysis-tasks/${id}/artifacts`),

  followUp: (id: string, question: string, evidenceIds: string[] = []) =>
    request<CreateTaskResponse>(`/analysis-tasks/${id}/follow-ups`, {
      method: "POST",
      body: JSON.stringify({
        question,
        referenced_evidence_ids: evidenceIds,
      }),
    }),

  submitClarification: (id: string, response: string) =>
    request<TaskDetail>(`/analysis-tasks/${id}/clarifications`, {
      method: "POST",
      body: JSON.stringify({ response }),
    }),

  giveFeedback: (id: string, rating: number, comment: string) =>
    request<{ saved: boolean }>(`/analysis-tasks/${id}/feedback`, {
      method: "POST",
      body: JSON.stringify({ rating, comment }),
    }),

  replay: (id: string) =>
    request<{ status: string }>(`/analysis-tasks/${id}/replay`, {
      method: "POST",
    }),
};

// Evaluation
export const evaluationApi = {
  get: () => request<EvaluationData>("/evaluation"),

  run: () => request<EvaluationRun>("/evaluation/run", {
    method: "POST",
  }),
};

// Semantic
export const semanticApi = {
  get: () => request<SemanticData>("/semantic"),
};

// Settings
export const settingsApi = {
  get: () => request<SettingsData>("/settings"),
};

// Export types
export { ApiError };
export type {
  HomeData,
  DataStatus,
  AnalysisTaskList,
  CreateTaskRequest,
  CreateTaskResponse,
  EvaluationData,
  EvaluationRun,
};
