"use client";

import { useState } from "react";
import { useAnalyzeRuntimeFinancialsMutation } from "@/queries/use-runtime-run";
import type { RuntimeRun } from "@/services/research-runtime-service";

export function FinancialAnalysisForm({ run }: { run: RuntimeRun }) {
  const mutation = useAnalyzeRuntimeFinancialsMutation(run.id);
  const qualifiedEvidence = run.evidence.filter((item) => item.qualification === "QUALIFIED");
  const [period, setPeriod] = useState("FY2025");
  const [revenue, setRevenue] = useState("");
  const [priorRevenue, setPriorRevenue] = useState("");
  const [revenueEvidenceId, setRevenueEvidenceId] = useState("");
  const [priorRevenueEvidenceId, setPriorRevenueEvidenceId] = useState("");

  if (qualifiedEvidence.length === 0) return <section className="decision-panel financial-analysis-form"><header><div><small>CALCULATION INPUT</small><h2>Financial analysis</h2></div><span>evidence-gated</span></header><p className="form-note">Financial analysis requires qualified evidence from this run.</p></section>;

  const canSubmit = period.trim().length > 0 && revenue.trim().length > 0 && revenueEvidenceId.length > 0 && (!priorRevenue.trim() || priorRevenueEvidenceId.length > 0);
  const evidenceLabel = (id: string) => qualifiedEvidence.find((item) => item.id === id)?.source_title ?? "Qualified evidence";

  function submit(event: React.FormEvent<HTMLFormElement>) {
    event.preventDefault();
    if (!canSubmit || mutation.isPending) return;
    const evidenceIds: Record<string, string[]> = { revenue: [revenueEvidenceId] };
    const snapshot: { period: string; revenue: string; prior_revenue?: string } = { period: period.trim(), revenue: revenue.trim() };
    if (priorRevenue.trim()) {
      snapshot.prior_revenue = priorRevenue.trim();
      evidenceIds.prior_revenue = [priorRevenueEvidenceId];
    }
    mutation.mutate({ snapshot, evidence_ids: evidenceIds });
  }

  return <section className="decision-panel financial-analysis-form">
    <header><div><small>CALCULATION INPUT</small><h2>Financial analysis</h2></div><span>{qualifiedEvidence.length} qualified evidence</span></header>
    <form onSubmit={submit}>
      <div className="financial-analysis-grid">
        <label htmlFor="runtime-financial-period">Period<input id="runtime-financial-period" className="text-control" value={period} onChange={(event) => setPeriod(event.target.value)} required /></label>
        <label htmlFor="runtime-financial-revenue">Revenue<input id="runtime-financial-revenue" className="text-control" type="text" inputMode="decimal" pattern="[0-9]+(\.[0-9]+)?" value={revenue} onChange={(event) => setRevenue(event.target.value)} required /></label>
        <label htmlFor="runtime-financial-revenue-evidence">Revenue evidence<select id="runtime-financial-revenue-evidence" className="text-control" value={revenueEvidenceId} onChange={(event) => setRevenueEvidenceId(event.target.value)} required><option value="">Select qualified evidence…</option>{qualifiedEvidence.map((item) => <option key={item.id} value={item.id}>{evidenceLabel(item.id)} · {item.stance} · {item.id}</option>)}</select></label>
        <label htmlFor="runtime-financial-prior-revenue">Prior revenue <span>(optional)</span><input id="runtime-financial-prior-revenue" className="text-control" type="text" inputMode="decimal" pattern="[0-9]+(\.[0-9]+)?" value={priorRevenue} onChange={(event) => setPriorRevenue(event.target.value)} /></label>
        {priorRevenue.trim() && <label htmlFor="runtime-financial-prior-evidence">Prior revenue evidence<select id="runtime-financial-prior-evidence" className="text-control" value={priorRevenueEvidenceId} onChange={(event) => setPriorRevenueEvidenceId(event.target.value)} required><option value="">Select qualified evidence…</option>{qualifiedEvidence.map((item) => <option key={item.id} value={item.id}>{evidenceLabel(item.id)} · {item.stance} · {item.id}</option>)}</select></label>}
      </div>
      <p className="form-note">Enter values explicitly. Metrics are calculated only from these inputs and remain linked to qualified evidence.</p>
      {mutation.isError && <p className="form-error" role="alert">{mutation.error.message}</p>}
      {mutation.isSuccess && <p className="form-success" role="status">Analysis saved to this run.</p>}
      <div className="form-actions"><button type="submit" className="blue-button" disabled={!canSubmit || mutation.isPending}>{mutation.isPending ? "Saving…" : "Save analysis"}</button></div>
    </form>
  </section>;
}
