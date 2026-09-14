import Link from "next/link";
import type { RuntimeRun } from "@/services/research-runtime-service";

function formatDate(value: string | undefined): string {
  if (!value) return "Date unavailable";
  const date = new Date(value);
  return Number.isNaN(date.getTime()) ? "Date unavailable" : date.toLocaleString();
}

export function RuntimeCaseHistory({ runs, activeRunId, isPending, error }: { runs: RuntimeRun[] | undefined; activeRunId: string; isPending: boolean; error: Error | null }) {
  return <section className="decision-panel runtime-case-history" aria-labelledby="runtime-case-history-heading">
    <header><div><small>RESEARCH CASE · DURABLE HISTORY</small><h2 id="runtime-case-history-heading">Run history</h2></div><span>{runs?.length ?? 0} runs</span></header>
    {isPending && <p className="form-note">Loading case history…</p>}
    {error && <p className="form-error" role="alert">Run history unavailable: {error.message}</p>}
    {!isPending && !error && runs?.length === 0 && <p className="empty-state">No durable runs are recorded for this ResearchCase.</p>}
    {!isPending && !error && runs && runs.length > 0 && <div className="runtime-case-history-list">{runs.map((run) => <article className={`runtime-case-history-row ${run.id === activeRunId ? "active" : ""}`} key={run.id}><div><strong>{run.id}</strong><small>{run.id === activeRunId ? "Active run" : "Historical run"} · {formatDate(run.created_at)}</small></div><span className={`thesis-state ${run.state.toLowerCase()}`}>{run.state}</span><Link className="link-button" href={`/runtime/${encodeURIComponent(run.id)}`}>{run.id === activeRunId ? "Open current" : "Open run"}</Link></article>)}</div>}
  </section>;
}
