"use client";

import { useEffect } from "react";
import { useRouter } from "next/navigation";
import { AppShell } from "@/components/shell/app-shell";
import { useRuntimeCaseRunsQuery } from "@/queries/use-runtime-run";

export function RuntimeCaseBridge({ caseId }: { caseId: string }) {
  const router = useRouter();
  const runs = useRuntimeCaseRunsQuery(caseId);
  const latestRun = runs.data?.at(-1);

  useEffect(() => {
    if (latestRun) router.replace(`/runtime/${encodeURIComponent(latestRun.id)}`);
  }, [latestRun, router]);

  if (runs.isPending) return <AppShell context={<div />}><div className="skeleton-stack"><i /><i /><i /></div></AppShell>;
  if (runs.isError) return <AppShell context={<div />}><div className="error-state" role="alert"><b>Research case could not be loaded</b><span>{runs.error.message}</span><button type="button" onClick={() => runs.refetch()}>Retry</button></div></AppShell>;
  if (!latestRun) return <AppShell context={<div />}><div className="error-state" role="alert"><b>No durable run exists for this case</b><span>Create a new case from the live runtime workspace before opening this link.</span></div></AppShell>;
  return <AppShell context={<div />}><div className="skeleton-stack"><i /><i /><i /></div></AppShell>;
}
