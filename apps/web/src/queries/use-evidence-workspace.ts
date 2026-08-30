"use client";

import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import type { Evidence, RequestMoreResearchInput, ReviewClaimInput } from "@/domain/research";
import { researchRepository } from "@/repositories";

export const evidenceQueryKey = (caseId: string) => ["research", "evidence", caseId] as const;
export function useEvidenceWorkspaceQuery(caseId: string) { return useQuery({ queryKey: evidenceQueryKey(caseId), queryFn: () => researchRepository.getEvidenceWorkspace(caseId) }); }
function useEvidenceMutation<T>(caseId: string, mutationFn: (input: T) => ReturnType<typeof researchRepository.getEvidenceWorkspace>) {
  const queryClient = useQueryClient();
  return useMutation({ mutationFn, onSuccess: (data) => queryClient.setQueryData(evidenceQueryKey(caseId), data) });
}
export function useUpdateEvidenceStatusMutation(caseId: string) { return useEvidenceMutation(caseId, (input: { evidenceId: string; status: Evidence["verificationStatus"] }) => researchRepository.updateEvidenceStatus({ caseId, ...input })); }
export function useReviewClaimMutation(caseId: string) { return useEvidenceMutation(caseId, (input: Omit<ReviewClaimInput, "caseId">) => researchRepository.reviewClaim({ caseId, ...input })); }
export function useRequestMoreResearchMutation(caseId: string) { return useEvidenceMutation(caseId, (input: Omit<RequestMoreResearchInput, "caseId">) => researchRepository.requestMoreResearch({ caseId, ...input })); }
