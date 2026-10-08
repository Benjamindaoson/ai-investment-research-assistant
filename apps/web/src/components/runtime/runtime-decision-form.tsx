"use client";

import { useState } from "react";
import { useRecordRuntimeDecisionMutation } from "@/queries/use-runtime-run";
import type { DecisionRecordInput, RuntimeRun } from "@/services/research-runtime-service";

const actions: Array<[DecisionRecordInput["action"], string]> = [
  ["APPROVE_THESIS", "Approve thesis"],
  ["REJECT_THESIS", "Reject thesis"],
  ["REQUEST_RESEARCH", "Request more research"],
];

export function RuntimeDecisionForm({ run }: { run: RuntimeRun }) {
  const mutation = useRecordRuntimeDecisionMutation(run.id);
  const [actor, setActor] = useState("Analyst");
  const [action, setAction] = useState<DecisionRecordInput["action"]>("APPROVE_THESIS");
  const [rationale, setRationale] = useState("");
  const [reviewIds, setReviewIds] = useState<string[]>([]);
  const thesis = run.thesis;
  if (!thesis) return null;
  const thesisId = thesis.id;

  const approvalUnavailable = action === "APPROVE_THESIS" && run.state !== "COMPLETED";
  const canSubmit = actor.trim().length > 0 && rationale.trim().length >= 3 && !approvalUnavailable && !mutation.isPending;

  function submit(event: React.FormEvent<HTMLFormElement>) {
    event.preventDefault();
    if (!canSubmit) return;
    mutation.mutate({ actor: actor.trim(), action, target_id: thesisId, rationale: rationale.trim(), review_ids: reviewIds });
  }

  return (
    <section className="decision-panel runtime-decision-form">
      <header><div><small>HUMAN REVIEW · WRITE-ONCE DECISION</small><h2>Review thesis</h2></div><span>{thesis.review_status}</span></header>
      <p className="form-note">This decision targets thesis <b>{thesisId}</b>. Backend rules remain authoritative.</p>
      <form onSubmit={submit}>
        <div className="runtime-decision-grid">
          <label htmlFor="runtime-decision-actor">Analyst<input id="runtime-decision-actor" className="text-control" value={actor} onChange={(event) => setActor(event.target.value)} required /></label>
          <label htmlFor="runtime-decision-action">Action<select id="runtime-decision-action" className="text-control" value={action} onChange={(event) => setAction(event.target.value as DecisionRecordInput["action"])}>{actions.map(([value, label]) => <option value={value} key={value} disabled={value === "APPROVE_THESIS" && run.state !== "COMPLETED"}>{label}</option>)}</select></label>
          {run.ic_reviews.length > 0 && <label htmlFor="runtime-decision-reviews">IC reviews considered<select id="runtime-decision-reviews" className="text-control red-team-evidence-select" multiple size={Math.min(4, run.ic_reviews.length)} value={reviewIds} onChange={(event) => setReviewIds(Array.from(event.target.selectedOptions, (option) => option.value))}><option value="" disabled>Select reviews</option>{run.ic_reviews.map((review) => <option key={review.id} value={review.id}>{review.role} · {review.recommendation} · {review.reviewer}</option>)}</select><small>Optional for compatibility; selecting records makes the decision basis explicit.</small></label>}
          <label htmlFor="runtime-decision-rationale">Rationale<textarea id="runtime-decision-rationale" className="text-control" rows={4} value={rationale} onChange={(event) => setRationale(event.target.value)} placeholder="Record the reasoning that should remain in the audit trail." required /></label>
        </div>
        {run.state !== "COMPLETED" && <p className="form-note">Approval becomes available after the run reaches COMPLETED. Rejection or a research request can still be recorded when eligible.</p>}
        {mutation.isError && <p className="form-error" role="alert">{mutation.error.message}</p>}
        {mutation.isSuccess && <p className="form-success" role="status">Decision recorded in the runtime audit trail.</p>}
        <div className="form-actions"><button type="submit" className="blue-button" disabled={!canSubmit}>{mutation.isPending ? "Recording decision…" : "Record decision"}</button></div>
      </form>
    </section>
  );
}
