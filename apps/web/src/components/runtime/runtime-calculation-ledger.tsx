import type { CalculationLedgerEntry } from "@/services/research-runtime-service";

function label(metric: string) {
  return metric.replaceAll("_", " ");
}

export function RuntimeCalculationLedger({ entries }: { entries: CalculationLedgerEntry[] }) {
  return (
    <section className="decision-panel" aria-label="Calculation ledger">
      <header><div><small>CALCULATION LEDGER · READ-ONLY</small><h2>How each metric was calculated</h2></div><span>{entries.length ? `${entries.length} metrics` : "not available"}</span></header>
      {entries.length === 0 ? <p className="form-note">Calculation ledger is unavailable for this historical artifact; no formulas or values were fabricated.</p> : <div className="runtime-calculation-ledger" role="list">
        {entries.map((entry) => <article className="memo-section" key={entry.metric} role="listitem">
          <header><h3>{label(entry.metric)}</h3><span>{entry.status}</span></header>
          <p><b>Formula:</b> {entry.formula}</p>
          <p><b>Inputs:</b> {Object.entries(entry.inputs).map(([key, value]) => `${key}=${value}`).join(" · ") || "none"}</p>
          <p><b>Output:</b> {entry.value ?? "Unavailable"} {entry.value === null ? "" : entry.unit}</p>
          {entry.reason && <small>Reason: {entry.reason}</small>}
          {entry.evidence_ids.length > 0 && <small>Evidence: {entry.evidence_ids.join(", ")}</small>}
        </article>)}
      </div>}
    </section>
  );
}
