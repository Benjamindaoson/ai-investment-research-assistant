"use client";

import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import type { ResearchFinding, ResearchPlan, ResearchRunAction } from "@/domain/research";
import { researchRepository } from "@/repositories";

export const researchCaseQueryKey = (caseId: string) => ["research", "case", caseId] as const;

export function useResearchCaseQuery(caseId: string) {
  return useQuery({ queryKey: researchCaseQueryKey(caseId), queryFn: () => researchRepository.getResearchCase(caseId) });
}

export function useUpdateResearchPlanMutation(caseId: string) {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (plan: ResearchPlan) => researchRepository.updateResearchPlan({ caseId, plan }),
    onSuccess: (data) => queryClient.setQueryData(researchCaseQueryKey(caseId), data),
  });
}

export function useResearchRunControlMutation(caseId: string) {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (action: ResearchRunAction) => researchRepository.controlResearchRun({ caseId, action }),
    onSuccess: (data) => queryClient.setQueryData(researchCaseQueryKey(caseId), data),
  });
}

export function useUpdateFindingMutation(caseId: string) {
  const queryClient = useQueryClient();
  return useMutation({ mutationFn: (finding: ResearchFinding) => researchRepository.updateFinding({ caseId, finding }), onSuccess: (data) => queryClient.setQueryData(researchCaseQueryKey(caseId), data) });
}
