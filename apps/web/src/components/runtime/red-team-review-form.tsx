"use client";

import { useState } from "react";
import { useCreateRedTeamReviewMutation } from "@/queries/use-runtime-run";
import type { RuntimeRun } from "@/services/research-runtime-service";

const outcomes = [
  ["OPEN", "Open challenge"],
  ["SUPPORTED", "Challenge supported"],
  ["REJECTED", "Challenge rejected"],
  ["REQUIRES_RESEARCH", "Requires more research"],
] as const;

export function RedTeamReviewForm({ run }: { run: RuntimeRun }) {
  const mutation = useCreateRedTeamReviewMutation(run.id);
  const disconfirmingEvidence = run.evidence.filter((item) => item.stance === "COUNTER" || item.stance === "CONFLICTING");
  const [reviewer, setReviewer] = useState("Investment analyst");
  const [challenge, setChallenge] = useState("");
  const [rationale, setRationale] = useState("");
  const [outcome, setOutcome] = useState<(typeof outcomes)[number][0]>("REQUIRES_RESEARCH");
  const [evidenceIds, setEvidenceIds] = useState<string[]>([]);

  if (!run.thesis || disconfirmingEvidence.length === 0) return null;

  const canSubmit = reviewer.trim().length > 0 && challenge.trim().length > 0 && rationale.trim().length > 0 && evidenceIds.length > 0;
  const evidenceLabel = (id: string) => disconfirmingEvidence.find((item) => item.id === id)?.source_title ?? "Disconfirming evidence";

  function submit(event: React.FormEvent<HTMLFormElement>) {
    event.preventDefault();
    if (!canSubmit || mutation.isPending) return;
    mutation.mutate({ reviewer: reviewer.trim(), challenge: challenge.trim(), rationale: rationale.trim(), outcome, evidence_ids: evidenceIds });
  }

  return <section className="decision-panel red-team-review-form">
    <header><div><small>RED-TEAM REVIEW</small><h2>Challenge the thesis</h2></div><span>{disconfirmingEvidence.length} disconfirming evidence</span></header>
    <form onSubmit={submit}>
      <div className="red-team-grid">
        <label htmlFor="runtime-reviewer">Reviewer<input id="runtime-reviewer" className="text-control" value={reviewer} onChange={(event) => setReviewer(event.target.value)} required /></label>
        <label htmlFor="runtime-review-outcome">Outcome<select id="runtime-review-outcome" className="text-control" value={outcome} onChange={(event) => setOutcome(event.target.value as (typeof outcomes)[number][0])} required>{outcomes.map(([value, label]) => <option key={value} value={value}>{label}</option>)}</select></label>
        <label htmlFor="runtime-review-evidence">Disconfirming evidence<select id="runtime-review-evidence" className="text-control red-team-evidence-select" multiple size={Math.min(4, disconfirmingEvidence.length)} value={evidenceIds} onChange={(event) => setEvidenceIds(Array.from(event.target.selectedOptions, (option) => option.value))} required>{disconfirmingEvidence.map((item) => <option key={item.id} value={item.id}>{evidenceLabel(item.id)} · {item.stance} · {item.id}</option>)}</select><small>Select one or more counter or conflicting records.</small></label>
        <label htmlFor="runtime-review-challenge">Challenge<textarea id="runtime-review-challenge" className="text-control" rows={3} value={challenge} onChange={(event) => setChallenge(event.target.value)} placeholder="What could invalidate the current thesis?" required /></label>
        <label htmlFor="runtime-review-rationale">Rationale<textarea id="runtime-review-rationale" className="text-control" rows={3} value={rationale} onChange={(event) => setRationale(event.target.value)} placeholder="Explain why the selected evidence supports this outcome." required /></label>
      </div>
      {mutation.isError && <p className="form-error" role="alert">{mutation.error.message}</p>}
      {mutation.isSuccess && <p className="form-success" role="status">Red-team review saved to this run.</p>}
      <div className="form-actions"><button type="submit" className="blue-button" disabled={!canSubmit || mutation.isPending}>{mutation.isPending ? "Saving review…" : "Save red-team review"}</button></div>
    </form>
  </section>;
}
