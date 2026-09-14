import type { RuntimeEvidence } from "@/services/research-runtime-service";

function evidenceTitle(evidence: RuntimeEvidence): string {
  return evidence.source_title ?? evidence.source_id ?? "Source unavailable";
}

export function RuntimeEvidenceTrace({ evidence }: { evidence: RuntimeEvidence[] }) {
  return (
    <section className="decision-panel runtime-evidence-trace">
      <header><div><small>EVIDENCE TRACE · READ-ONLY</small><h2>Observed source records</h2></div><span>{evidence.length} records</span></header>
      <div className="runtime-evidence-list">
        {evidence.length === 0 && <p className="form-note">No evidence records returned for this run.</p>}
        {evidence.map((item, index) => {
          const provenanceComplete = Boolean(item.source_url && item.locator && item.content_hash);
          return <article className={`runtime-evidence-record ${item.stance.toLowerCase()}`} key={`${item.id}-${index}`}>
            <header><div><b>{evidenceTitle(item)}</b><small>{item.provider ?? "Provider unavailable"} · {item.id}</small></div><div className="runtime-evidence-badges"><span>{item.stance}</span><span>{item.qualification}</span></div></header>
            <p>{item.excerpt ?? "Excerpt unavailable from this response."}</p>
            <footer><span>{item.task_id ?? "Task unavailable"} · {item.requirement_id ?? "Requirement unavailable"}</span>{item.source_url && <a href={item.source_url} target="_blank" rel="noreferrer">Open source</a>}{item.locator && <span>Locator: {item.locator}</span>}{item.content_hash && <span>Hash: {item.content_hash}</span>}<span className={provenanceComplete ? "provenance-complete" : "provenance-incomplete"}>{provenanceComplete ? "Provenance complete" : "Provenance incomplete"}</span></footer>
          </article>;
        })}
      </div>
    </section>
  );
}
