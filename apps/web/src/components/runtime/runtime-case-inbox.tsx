import Link from "next/link";
import type { RuntimeResearchCase } from "@/services/research-runtime-service";

type CaseInboxItem = RuntimeResearchCase & { latest_run_id: string | null };

function formatDate(value: string | undefined): string {
  if (!value) return "Date unavailable";
  const date = new Date(value);
  return Number.isNaN(date.getTime()) ? "Date unavailable" : date.toLocaleString();
}

export function RuntimeCaseInbox({ cases, isPending, error }: { cases: CaseInboxItem[] | undefined; isPending: boolean; error: Error | null }) {
  return <section className="decision-panel runtime-case-inbox" aria-labelledby="runtime-case-inbox-heading">
    <header><div><small>RESEARCH OPERATING SYSTEM · DURABLE CASES</small><h2 id="runtime-case-inbox-heading">Existing research cases</h2></div><span>{cases?.length ?? 0} cases</span></header>
    {isPending && <p className="form-note">Loading research cases…</p>}
    {error && <p className="form-error" role="alert">Cases unavailable: {error.message}</p>}
    {!isPending && !error && cases?.length === 0 && <p className="empty-state">No durable ResearchCases yet. Create the first one below.</p>}
    {!isPending && !error && cases && cases.length > 0 && <div className="runtime-case-inbox-list">{cases.map((researchCase) => <article key={researchCase.id}><div><strong>{researchCase.target}</strong><small>{researchCase.id} · {formatDate(researchCase.created_at)}</small></div><p>{researchCase.question}</p><span>{researchCase.mandate.decision_type}</span>{researchCase.latest_run_id ? <Link className="link-button" href={`/runtime/${encodeURIComponent(researchCase.latest_run_id)}`}>Open latest run</Link> : <small>No run yet</small>}</article>)}</div>}
  </section>;
}
