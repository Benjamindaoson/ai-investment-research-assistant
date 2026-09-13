"use client";

import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { researchRuntimeRepository } from "@/repositories";
import type { RuntimeCaseInput } from "@/services/research-runtime-service";

export const runtimeRunQueryKey = (runId: string) => ["runtime", "run", runId] as const;

export function useCreateRuntimeCaseMutation() {
  return useMutation({ mutationFn: (input: RuntimeCaseInput) => researchRuntimeRepository.createCase(input) });
}

export function useRuntimeRunQuery(runId: string) {
  return useQuery({ queryKey: runtimeRunQueryKey(runId), queryFn: () => researchRuntimeRepository.getRun(runId) });
}

export function useExecuteRuntimeRunMutation(runId: string) {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: () => researchRuntimeRepository.executeRun(runId),
    onSuccess: (data) => queryClient.setQueryData(runtimeRunQueryKey(runId), data),
  });
}

export function useCancelRuntimeRunMutation(runId: string) {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (reason: string) => researchRuntimeRepository.cancelRun(runId, reason),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: runtimeRunQueryKey(runId) }),
  });
}
