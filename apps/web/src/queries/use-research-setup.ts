"use client";

import { useMutation, useQuery } from "@tanstack/react-query";
import type { CreateResearchCaseInput, ResearchSetup } from "@/domain/research";
import { researchRepository } from "@/repositories";

export function useResearchSetupOptionsQuery() {
  return useQuery({
    queryKey: ["research", "setup-options"],
    queryFn: () => researchRepository.getResearchSetupOptions(),
    staleTime: Number.POSITIVE_INFINITY,
  });
}

export function useProposeResearchPlanMutation() {
  return useMutation({ mutationFn: (input: ResearchSetup) => researchRepository.proposeResearchPlan(input) });
}

export function useCreateResearchCaseMutation() {
  return useMutation({ mutationFn: (input: CreateResearchCaseInput) => researchRepository.createResearchCase(input) });
}
