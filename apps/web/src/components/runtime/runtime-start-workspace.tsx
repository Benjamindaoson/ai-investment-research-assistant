"use client";

import { useRouter } from "next/navigation";
import { useState } from "react";
import { AppShell } from "@/components/shell/app-shell";
import { RuntimeCaseInbox } from "@/components/runtime/runtime-case-inbox";
import { useCreateRuntimeCaseMutation, useRuntimeCasesQuery } from "@/queries/use-runtime-run";
import type { ResearchMandate } from "@/services/research-runtime-service";

const defaultQuestion = "Assess ACME margin durability using supporting and disconfirming evidence.";

const decisionTypes: Array<[ResearchMandate["decision_type"], string]> = [
  ["INVESTMENT_COMMITTEE", "Investment committee"],
  ["DUE_DILIGENCE", "Due diligence"],
  ["SCREENING", "Screening"],
  ["MONITORING", "Monitoring"],
  ["STRATEGIC_REVIEW", "Strategic review"],
];

type RuntimeStartWorkspaceProps = {
  initialQuestion?: string;
  initialTarget?: string;
};

function normalizeInitialValue(value: string | undefined): string | undefined {
  const trimmed = value?.trim();
  return trimmed ? trimmed : undefined;
}

function splitEntries(value: string): string[] {
  return value.split(/[,\n]/).map((item) => item.trim()).filter(Boolean);
}

export function RuntimeStartWorkspace({ initialQuestion, initialTarget }: RuntimeStartWorkspaceProps = {}) {
  const router = useRouter();
  const createCase = useCreateRuntimeCaseMutation();
  const [target, setTarget] = useState(() => normalizeInitialValue(initialTarget) ?? "ACME");
  const [question, setQuestion] = useState(() => normalizeInitialValue(initialQuestion) ?? defaultQuestion);
  const [decisionType, setDecisionType] = useState<ResearchMandate["decision_type"]>("INVESTMENT_COMMITTEE");
  const [timeHorizon, setTimeHorizon] = useState("12 months");
  const [materiality, setMateriality] = useState<ResearchMandate["materiality"]>("MEDIUM");
  const [requiredOutputs, setRequiredOutputs] = useState("investment memo");
  const [constraints, setConstraints] = useState("");
  const configured = Boolean(process.env.NEXT_PUBLIC_RESEARCH_RUNTIME_URL);
  const casesQuery = useRuntimeCasesQuery(configured);

  async function submit() {
    const result = await createCase.mutateAsync({
      target,
      question,
      mandate: {
        decision_type: decisionType,
        time_horizon: timeHorizon.trim(),
        materiality,
        required_outputs: splitEntries(requiredOutputs),
        constraints: splitEntries(constraints),
      },
    });
    router.push(`/runtime/${result.run_id}`);
  }

  return (
    <AppShell context={<><div className="context-heading"><b>Live Research Runtime</b><span>{configured ? "Connected" : "Not configured"}</span></div><p className="context-note">The backend remains the source of truth for plan, evidence, and memo state.</p></>}>
      <div className="page-title"><div><p>LIVE RUNTIME · NEW CASE</p><h1>Start a canonical research run</h1><span>Use the durable backend workflow when a Research Runtime URL is configured.</span></div></div>
      {!configured && <div className="error-state" role="alert"><b>Research Runtime URL is not configured</b><span>Set NEXT_PUBLIC_RESEARCH_RUNTIME_URL before using this live workspace. The existing workspace remains explicitly synthetic.</span></div>}
      {configured && <RuntimeCaseInbox cases={casesQuery.data} isPending={casesQuery.isPending} error={casesQuery.error} />}
      <section className="setup-section">
        <header><h2>Target</h2><p>Use the backend target identity for Investment Memory grouping.</p></header>
        <div><input className="text-control" value={target} onChange={(event) => setTarget(event.target.value)} aria-label="Runtime target" /></div>
      </section>
      <section className="setup-section">
        <header><h2>Investment question</h2><p>The question is hashed into the canonical research plan input.</p></header>
        <div><textarea value={question} onChange={(event) => setQuestion(event.target.value)} rows={5} aria-label="Runtime investment question" /></div>
      </section>
      <section className="setup-section runtime-mandate-section">
        <header><h2>Research mandate</h2><p>Set the decision context before planning. These fields are preserved verbatim and are not inferred by the runtime.</p></header>
        <div className="runtime-mandate-grid">
          <label htmlFor="runtime-decision-type">Decision type<select id="runtime-decision-type" className="text-control" value={decisionType} onChange={(event) => setDecisionType(event.target.value as ResearchMandate["decision_type"])}>{decisionTypes.map(([value, label]) => <option value={value} key={value}>{label}</option>)}</select></label>
          <label htmlFor="runtime-time-horizon">Time horizon<input id="runtime-time-horizon" className="text-control" value={timeHorizon} onChange={(event) => setTimeHorizon(event.target.value)} placeholder="e.g. 36 months" /></label>
          <label htmlFor="runtime-materiality">Materiality<select id="runtime-materiality" className="text-control" value={materiality} onChange={(event) => setMateriality(event.target.value as ResearchMandate["materiality"])}><option value="LOW">Low</option><option value="MEDIUM">Medium</option><option value="HIGH">High</option></select></label>
          <label htmlFor="runtime-required-outputs">Required outputs<textarea id="runtime-required-outputs" className="text-control" rows={3} value={requiredOutputs} onChange={(event) => setRequiredOutputs(event.target.value)} placeholder="One output per line or comma-separated" /><small>Examples: investment memo, valuation sensitivity</small></label>
          <label htmlFor="runtime-constraints">Constraints<textarea id="runtime-constraints" className="text-control" rows={3} value={constraints} onChange={(event) => setConstraints(event.target.value)} placeholder="One constraint per line" /><small>Leave blank when there are no explicit constraints.</small></label>
        </div>
      </section>
      {createCase.isError && <p className="form-error" role="alert">{createCase.error.message}</p>}
      <div className="form-actions"><button type="button" className="blue-button" disabled={!configured || target.trim().length === 0 || question.trim().length < 3 || timeHorizon.trim().length === 0 || splitEntries(requiredOutputs).length === 0 || createCase.isPending} onClick={submit}>{createCase.isPending ? "Creating run…" : "Create runtime case"}</button></div>
    </AppShell>
  );
}
