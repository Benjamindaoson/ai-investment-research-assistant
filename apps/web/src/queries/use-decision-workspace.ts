"use client";

import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import type { DecisionItem, StructuredThesis } from "@/domain/research";
import { researchRepository } from "@/repositories";

export const decisionQueryKey = (companyId: string) => ["research", "decision", companyId] as const;
export function useDecisionWorkspaceQuery(companyId = "northstar") { return useQuery({ queryKey: decisionQueryKey(companyId), queryFn: () => researchRepository.getDecisionWorkspace(companyId) }); }
export function useUpdateThesisMutation(companyId = "northstar") { const client = useQueryClient(); return useMutation({ mutationFn: (thesis: StructuredThesis) => researchRepository.updateThesis({ companyId, thesis }), onSuccess: (data) => client.setQueryData(decisionQueryKey(companyId), data) }); }
export function useUpsertDecisionItemMutation(companyId = "northstar") { const client = useQueryClient(); return useMutation({ mutationFn: (item: DecisionItem) => researchRepository.upsertDecisionItem({ companyId, item }), onSuccess: (data) => client.setQueryData(decisionQueryKey(companyId), data) }); }
