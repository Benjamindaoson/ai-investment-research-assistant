"use client";

import { useState } from "react";
import type { FormEvent } from "react";
import type { RuntimeRun, ValuationScenarioInput } from "@/services/research-runtime-service";
import { useAnalyzeRuntimeValuationMutation } from "@/queries/use-runtime-run";

type ScenarioName = "BULL" | "BASE" | "BEAR";
type AssumptionField = "revenue_growth_pct" | "operating_margin_pct" | "fcf_margin_pct" | "discount_rate_pct" | "terminal_growth_pct" | "net_cash" | "shares_outstanding";
type ScenarioDraft = { name: ScenarioName; evidenceId: string } & Record<AssumptionField, string>;
const fields: AssumptionField[] = ["revenue_growth_pct", "operating_margin_pct", "fcf_margin_pct", "discount_rate_pct", "terminal_growth_pct", "net_cash", "shares_outstanding"];
const labels: Record<AssumptionField, string> = {
  revenue_growth_pct: "Revenue growth (%)", operating_margin_pct: "Operating margin (%)", fcf_margin_pct: "FCF margin (%)",
  discount_rate_pct: "Discount rate (%)", terminal_growth_pct: "Terminal growth (%)", net_cash: "Net cash", shares_outstanding: "Shares outstanding",
};
const ranges: Partial<Record<AssumptionField, { min?: string; max?: string }>> = {
  revenue_growth_pct: { min: "-100", max: "1000" }, operating_margin_pct: { min: "-1000", max: "1000" },
  fcf_margin_pct: { min: "-1000", max: "1000" }, discount_rate_pct: { min: "0.000000001", max: "100" },
  terminal_growth_pct: { min: "-100", max: "99.999999999" }, shares_outstanding: { min: "0.000000001" },
};

function emptyScenario(name: ScenarioName): ScenarioDraft {
  return { name, evidenceId: "", revenue_growth_pct: "", operating_margin_pct: "", fcf_margin_pct: "", discount_rate_pct: "", terminal_growth_pct: "", net_cash: "", shares_outstanding: "" };
}

export function ValuationScenarioForm({ run }: { run: RuntimeRun }) {
  const mutation = useAnalyzeRuntimeValuationMutation(run.id);
  const qualifiedEvidence = run.evidence.filter((item) => item.qualification === "QUALIFIED");
  const [baseRevenue, setBaseRevenue] = useState("");
  const [baseEvidenceId, setBaseEvidenceId] = useState("");
  const [scenarios, setScenarios] = useState<ScenarioDraft[]>([emptyScenario("BULL"), emptyScenario("BASE"), emptyScenario("BEAR")]);
  const blocked = ["FAILED", "CANCELLED", "BLOCKED"].includes(run.state);
  const canSubmit = !blocked && baseRevenue.trim() !== "" && baseEvidenceId !== "" && scenarios.every((scenario) => scenario.evidenceId !== "" && fields.every((field) => scenario[field].trim() !== ""));

  function updateScenario(index: number, field: AssumptionField | "evidenceId", value: string) {
    setScenarios((current) => current.map((scenario, position) => position === index ? { ...scenario, [field]: value } : scenario));
  }

  function submit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    if (!canSubmit) return;
    const input: ValuationScenarioInput = {
      base_revenue: baseRevenue,
      base_revenue_evidence_ids: [baseEvidenceId],
      scenarios: scenarios.map(({ evidenceId, ...scenario }) => ({
        ...scenario,
        evidence_ids: Object.fromEntries(fields.map((field) => [field, [evidenceId]])),
      })),
    };
    mutation.mutate(input);
  }

  if (blocked) return null;
  return <section className="decision-panel valuation-scenario-form">
    <header><div><small>VALUATION INPUT · EXPLICIT ASSUMPTIONS</small><h2>Build Bull / Base / Bear scenarios</h2></div><span>Qualified evidence only</span></header>
    <form onSubmit={submit}>
      <div className="valuation-base-input"><label>Base revenue<input className="text-control" type="number" min="0" step="any" value={baseRevenue} onChange={(event) => setBaseRevenue(event.target.value)} inputMode="decimal" placeholder="e.g. 100.00" /></label><label>Base revenue evidence<select className="text-control" value={baseEvidenceId} onChange={(event) => setBaseEvidenceId(event.target.value)}><option value="">Select qualified evidence</option>{qualifiedEvidence.map((item) => <option value={item.id} key={item.id}>{item.source_title ?? item.id}</option>)}</select></label></div>
      <div className="valuation-scenario-input-grid">{scenarios.map((scenario, index) => <fieldset key={scenario.name}><legend>{scenario.name}</legend>{fields.map((field) => <label key={field}>{labels[field]}<input className="text-control" type="number" step="any" {...ranges[field]} value={scenario[field]} onChange={(event) => updateScenario(index, field, event.target.value)} inputMode="decimal" /></label>)}<label>Scenario evidence<select className="text-control" value={scenario.evidenceId} onChange={(event) => updateScenario(index, "evidenceId", event.target.value)}><option value="">Select qualified evidence</option>{qualifiedEvidence.map((item) => <option value={item.id} key={item.id}>{item.source_title ?? item.id}</option>)}</select></label></fieldset>)}</div>
      {qualifiedEvidence.length === 0 && <p className="form-note">No qualified evidence is available. Complete evidence qualification before entering a valuation.</p>}
      <div className="form-actions"><button type="submit" className="blue-button" disabled={!canSubmit || mutation.isPending}>{mutation.isPending ? "Saving scenarios…" : "Save valuation scenarios"}</button></div>
      {mutation.isError && <p className="form-error" role="alert">{mutation.error.message}</p>}
      {mutation.isSuccess && <p className="form-success" role="status">Valuation scenarios saved as a durable, evidence-linked artifact.</p>}
    </form>
  </section>;
}
