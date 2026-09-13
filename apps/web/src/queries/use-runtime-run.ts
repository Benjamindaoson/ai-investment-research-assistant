"use client";

import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { researchRuntimeRepository } from "@/repositories";
import type { EvidenceLinkedFinancialAnalysisInput, RedTeamReviewInput, RuntimeCaseInput, RuntimeRun } from "@/services/research-runtime-service";

export const runtimeRunQueryKey = (runId: string) => ["runtime", "run", runId] as const;
export const runtimeMemoryQueryKey = (runId: string) => ["runtime", "memory", runId] as const;

export function useCreateRuntimeCaseMutation() {
  return useMutation({ mutationFn: (input: RuntimeCaseInput) => researchRuntimeRepository.createCase(input) });
}

export function useRuntimeRunQuery(runId: string) {
  return useQuery({ queryKey: runtimeRunQueryKey(runId), queryFn: () => researchRuntimeRepository.getRun(runId) });
}

export function useRuntimeMemoryQuery(runId: string, enabled: boolean) {
  return useQuery({ queryKey: runtimeMemoryQueryKey(runId), queryFn: () => researchRuntimeRepository.getMemoryForRun(runId), enabled });
}

export function useExecuteRuntimeRunMutation(runId: string) {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: () => researchRuntimeRepository.executeRun(runId),
    onSuccess: (data) => {
      queryClient.setQueryData(runtimeRunQueryKey(runId), data);
      void queryClient.invalidateQueries({ queryKey: runtimeMemoryQueryKey(runId) });
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
    },
  });
}

export function useCancelRuntimeRunMutation(runId: string) {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (reason: string) => researchRuntimeRepository.cancelRun(runId, reason),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: runtimeRunQueryKey(runId) }),
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

export function useCreateRedTeamReviewMutation(runId: string) {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (input: RedTeamReviewInput) => researchRuntimeRepository.createRedTeamReview(runId, input),
    onSuccess: (data) => queryClient.setQueryData<RuntimeRun>(runtimeRunQueryKey(runId), data),
  });
}
