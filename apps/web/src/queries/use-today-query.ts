"use client";

import { useQuery } from "@tanstack/react-query";
import { researchRepository } from "@/repositories";

export const todayQueryKey = ["research", "today"] as const;

export function useTodayQuery() {
  return useQuery({ queryKey: todayQueryKey, queryFn: () => researchRepository.getToday(), staleTime: 60_000 });
}
