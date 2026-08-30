"use client";

import { AppShell } from "@/components/shell/app-shell";
import { useTodayQuery } from "@/queries/use-today-query";
import { TodayOverview } from "./today-overview";
import { TodayWorklist } from "./today-worklist";

export function TodayWorkspace() {
  const today = useTodayQuery();
  if (today.isPending) return <AppShell context={<OverviewSkeleton />}><WorklistSkeleton /></AppShell>;
  if (today.isError) return <AppShell context={<OverviewSkeleton />}><div className="error-state" role="alert"><b>Today could not be loaded</b><span>{today.error.message}</span><button type="button" onClick={() => today.refetch()}>Try again</button></div></AppShell>;
  return <AppShell context={<TodayOverview overview={today.data.overview} />}><TodayWorklist items={today.data.items} fixtureNotice={today.data.fixtureNotice} /></AppShell>;
}
function WorklistSkeleton() { return <div className="skeleton-stack" aria-label="Loading Today research"><i /><i /><i /><i /></div>; }
function OverviewSkeleton() { return <div className="skeleton-stack compact" aria-label="Loading Today overview"><i /><i /><i /></div>; }
