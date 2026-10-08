import type { RuntimeClaim, RuntimeEvidence } from "@/services/research-runtime-service";

export function RuntimeClaimTrace({ claims, evidence }: { claims: RuntimeClaim[]; evidence: RuntimeEvidence[] }) {
  const evidenceById = new Map(evidence.map((item) => [item.id, item]));

  return <section className="decision-panel runtime-claim-trace">
    <header><div><small>CLAIM TRACE · READ-ONLY</small><h2>Evidence-linked claims</h2></div><span>{claims.length} claims</span></header>
    <div className="runtime-claim-list">
      {claims.length === 0 && <p className="form-note">No claims returned for this run.</p>}
      {claims.map((claim) => {
        const unresolved = claim.evidence_ids.filter((id) => !evidenceById.has(id));
        return <article className={`runtime-claim-record ${claim.status.toLowerCase()}`} key={claim.id}>
          <header><div><b>{claim.statement ?? "Claim statement unavailable from this response."}</b><small>{claim.task_id ?? "Task unavailable"} · {claim.id}</small></div><span>{claim.status}</span></header>
          <p>{claim.confidence === undefined ? "Claim confidence unavailable." : `Claim confidence: ${(claim.confidence * 100).toFixed(1)}% · not investment advice.`}</p>
          <footer><span>Evidence: {claim.evidence_ids.length ? claim.evidence_ids.join(", ") : "none"}</span>{unresolved.length > 0 && <span className="claim-unresolved">Unresolved evidence: {unresolved.join(", ")}</span>}</footer>
        </article>;
      })}
    </div>
  </section>;
}
