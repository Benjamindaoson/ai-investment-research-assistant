"use client";

import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { researchRuntimeRepository } from "@/repositories";
import type { DecisionRecordInput, EvidenceLinkedFinancialAnalysisInput, InvestmentCommitteeReviewInput, RedTeamReviewInput, RuntimeCaseInput, RuntimeEvent, RuntimeHealth, RuntimeResearchCase, RuntimeRun, RuntimeTrace, ValuationScenarioInput } from "@/services/research-runtime-service";

export const runtimeRunQueryKey = (runId: string) => ["runtime", "run", runId] as const;
export const runtimeCaseRunsQueryKey = (caseId: string) => ["runtime", "case-runs", caseId] as const;
export const runtimeEvaluationQueryKey = (runId: string) => ["runtime", "evaluation", runId] as const;
export const runtimeHealthQueryKey = ["runtime", "health"] as const;
export const runtimeCasesQueryKey = ["runtime", "cases"] as const;
export const runtimeMemoryQueryKey = (runId: string) => ["runtime", "memory", runId] as const;
export const runtimeTraceQueryKey = (runId: string) => ["runtime", "trace", runId] as const;
export const runtimeEventsQueryKey = (runId: string) => ["runtime", "events", runId] as const;
export const runtimeIcReviewsQueryKey = (runId: string) => ["runtime", "ic-reviews", runId] as const;
export const RUNTIME_REFRESH_INTERVAL_MS = 2000;

const terminalRunStates = new Set<RuntimeRun["state"]>(["COMPLETED", "PARTIAL", "FAILED", "CANCELLED", "BLOCKED"]);

export function runtimeRefreshInterval(state: RuntimeRun["state"] | undefined): number | false {
  return state && !terminalRunStates.has(state) ? RUNTIME_REFRESH_INTERVAL_MS : false;
}

export function useCreateRuntimeCaseMutation() {
  return useMutation({ mutationFn: (input: RuntimeCaseInput) => researchRuntimeRepository.createCase(input) });
}

export function useRuntimeCasesQuery(enabled: boolean) {
  return useQuery({
    queryKey: runtimeCasesQueryKey,
    queryFn: async (): Promise<Array<RuntimeResearchCase & { latest_run_id: string | null }>> => {
      const cases = await researchRuntimeRepository.getCases();
      const runs = await Promise.all(cases.map((researchCase) => researchRuntimeRepository.getCaseRuns(researchCase.id)));
      return cases.map((researchCase, index) => ({ ...researchCase, latest_run_id: runs[index]?.at(-1)?.id ?? null }));
    },
    enabled,
  });
}

export function useCreateRuntimeRerunMutation(caseId: string) {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: () => researchRuntimeRepository.createCaseRun(caseId),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: runtimeCaseRunsQueryKey(caseId) }),
  });
}

export function useRuntimeRunQuery(runId: string) {
  return useQuery({
    queryKey: runtimeRunQueryKey(runId),
    queryFn: () => researchRuntimeRepository.getRun(runId),
    refetchInterval: (query) => runtimeRefreshInterval(query.state.data?.state),
  });
}

export function useRuntimeCaseRunsQuery(caseId: string) {
  return useQuery({ queryKey: runtimeCaseRunsQueryKey(caseId), queryFn: () => researchRuntimeRepository.getCaseRuns(caseId), enabled: caseId.length > 0 });
}

export function useRuntimeEvaluationQuery(runId: string) {
  return useQuery({ queryKey: runtimeEvaluationQueryKey(runId), queryFn: () => researchRuntimeRepository.getEvaluation(runId), enabled: runId.length > 0 });
}

export function useRuntimeHealthQuery(enabled: boolean) {
  return useQuery<RuntimeHealth>({ queryKey: runtimeHealthQueryKey, queryFn: () => researchRuntimeRepository.getHealth(), enabled, staleTime: 30_000 });
}

export function useRuntimeMemoryQuery(runId: string, enabled: boolean) {
  return useQuery({ queryKey: runtimeMemoryQueryKey(runId), queryFn: () => researchRuntimeRepository.getMemoryForRun(runId), enabled });
}

export function useRuntimeTraceQuery(runId: string) {
  return useQuery<RuntimeTrace>({
    queryKey: runtimeTraceQueryKey(runId),
    queryFn: () => researchRuntimeRepository.getTrace(runId),
    refetchInterval: (query) => runtimeRefreshInterval(query.state.data?.state),
  });
}

export function useRuntimeEventsQuery(runId: string, state: RuntimeRun["state"] | undefined) {
  return useQuery<RuntimeEvent[]>({
    queryKey: runtimeEventsQueryKey(runId),
    queryFn: () => researchRuntimeRepository.getEvents(runId),
    enabled: runId.length > 0,
    refetchInterval: runtimeRefreshInterval(state),
  });
}

export function useExecuteRuntimeRunMutation(runId: string) {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: () => researchRuntimeRepository.executeRun(runId),
    onSuccess: (data) => {
      queryClient.setQueryData(runtimeRunQueryKey(runId), data);
      void queryClient.invalidateQueries({ queryKey: runtimeMemoryQueryKey(runId) });
      void queryClient.invalidateQueries({ queryKey: runtimeTraceQueryKey(runId) });
      void queryClient.invalidateQueries({ queryKey: ["runtime", "case-runs"] });
    },
  });
}

export function useEnqueueRuntimeRunMutation(runId: string) {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: () => researchRuntimeRepository.enqueueRun(runId),
    onSuccess: () => {
      void queryClient.invalidateQueries({ queryKey: runtimeRunQueryKey(runId) });
      void queryClient.invalidateQueries({ queryKey: runtimeTraceQueryKey(runId) });
      void queryClient.invalidateQueries({ queryKey: runtimeEventsQueryKey(runId) });
      void queryClient.invalidateQueries({ queryKey: ["runtime", "case-runs"] });
    },
  });
}
export function useReplanRuntimeRunMutation(runId: string) {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: () => researchRuntimeRepository.replanRun(runId),
    onSuccess: (data) => {
      queryClient.setQueryData(runtimeRunQueryKey(runId), data);
      void queryClient.invalidateQueries({ queryKey: runtimeMemoryQueryKey(runId) });
      void queryClient.invalidateQueries({ queryKey: runtimeTraceQueryKey(runId) });
      void queryClient.invalidateQueries({ queryKey: ["runtime", "case-runs"] });
    },
  });
}

export function useCancelRuntimeRunMutation(runId: string) {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (reason: string) => researchRuntimeRepository.cancelRun(runId, reason),
    onSuccess: () => {
      void queryClient.invalidateQueries({ queryKey: runtimeRunQueryKey(runId) });
      void queryClient.invalidateQueries({ queryKey: runtimeTraceQueryKey(runId) });
      void queryClient.invalidateQueries({ queryKey: ["runtime", "case-runs"] });
    },
  });
}

export function useAnalyzeRuntimeFinancialsMutation(runId: string) {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (input: EvidenceLinkedFinancialAnalysisInput) => researchRuntimeRepository.analyzeFinancialsForRun(runId, input),
    onSuccess: (analysis) => {
      queryClient.setQueryData<RuntimeRun>(runtimeRunQueryKey(runId), (current) => current ? { ...current, financial_analysis: analysis } : current);
    },
  });
}

export function useAnalyzeRuntimeValuationMutation(runId: string) {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (input: ValuationScenarioInput) => researchRuntimeRepository.analyzeValuationScenarios(runId, input),
    onSuccess: (artifact) => queryClient.setQueryData<RuntimeRun>(runtimeRunQueryKey(runId), (current) => current ? { ...current, valuation_scenarios: artifact } : current),
  });
}

export function useCreateRedTeamReviewMutation(runId: string) {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (input: RedTeamReviewInput) => researchRuntimeRepository.createRedTeamReview(runId, input),
    onSuccess: (data) => queryClient.setQueryData<RuntimeRun>(runtimeRunQueryKey(runId), data),
  });
}

export function useCreateInvestmentCommitteeReviewMutation(runId: string) {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (input: InvestmentCommitteeReviewInput) => researchRuntimeRepository.createInvestmentCommitteeReview(runId, input),
    onSuccess: (data) => {
      queryClient.setQueryData(runtimeRunQueryKey(runId), data);
      void queryClient.invalidateQueries({ queryKey: runtimeIcReviewsQueryKey(runId) });
    },
  });
}

export function useRecordRuntimeDecisionMutation(runId: string) {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (input: DecisionRecordInput) => researchRuntimeRepository.recordDecision(runId, input),
    onSuccess: (data) => {
      queryClient.setQueryData(runtimeRunQueryKey(runId), data);
      void queryClient.invalidateQueries({ queryKey: runtimeMemoryQueryKey(runId) });
    },
  });
}
