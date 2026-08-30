"use client";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import type { LivingBrief, PerformReviewInput } from "@/domain/research";
import { researchRepository } from "@/repositories";
export const outputQueryKey = ["research", "outputs"] as const;
export function useOutputWorkspaceQuery() { return useQuery({ queryKey: outputQueryKey, queryFn: () => researchRepository.getOutputWorkspace() }); }
export function usePerformReviewMutation() { const client = useQueryClient(); return useMutation({ mutationFn: (input: PerformReviewInput) => researchRepository.performReview(input), onSuccess: (data) => client.setQueryData(outputQueryKey, data) }); }
export function useUpdateBriefMutation() { const client = useQueryClient(); return useMutation({ mutationFn: (brief: LivingBrief) => researchRepository.updateBrief({ brief }), onSuccess: (data) => client.setQueryData(outputQueryKey, data) }); }
