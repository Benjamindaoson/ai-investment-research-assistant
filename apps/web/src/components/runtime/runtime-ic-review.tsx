"use client";

import { useState } from "react";
import { useCreateInvestmentCommitteeReviewMutation } from "@/queries/use-runtime-run";
import type { InvestmentCommitteeReviewInput, RuntimeRun } from "@/services/research-runtime-service";

const roles: Array<[InvestmentCommitteeReviewInput["role"], string]> = [
  ["BULL", "Bull case"],
  ["BEAR", "Bear case"],
  ["FINANCIAL", "Financial"],
  ["INDUSTRY", "Industry"],
  ["PARTNER", "Partner"],
];

export function RuntimeIcReview({ run }: { run: RuntimeRun }) {
  const mutation = useCreateInvestmentCommitteeReviewMutation(run.id);
  const [role, setRole] = useState<InvestmentCommitteeReviewInput["role"]>("BULL");
  const [reviewer, setReviewer] = useState("Investment committee reviewer");
  const [position, setPosition] = useState<InvestmentCommitteeReviewInput["position"]>("MIXED");
  const [recommendation, setRecommendation] = useState<InvestmentCommitteeReviewInput["recommendation"]>("HOLD");
  const [rationale, setRationale] = useState("");
  const [evidenceIds, setEvidenceIds] = useState<string[]>([]);
  const reviewedRoles = new Set(run.ic_reviews.map((review) => review.role));
  const canSubmit = reviewer.trim().length > 0 && rationale.trim().length >= 3 && evidenceIds.length > 0;

  function submit(event: React.FormEvent<HTMLFormElement>) {
    event.preventDefault();
    if (!canSubmit || mutation.isPending) return;
    mutation.mutate({ role, reviewer: reviewer.trim(), position, recommendation, rationale: rationale.trim(), evidence_ids: evidenceIds });
  }

  return <section className="decision-panel runtime-ic-review">
    <header><div><small>IC REVIEW PANEL</small><h2>Record structured review</h2></div><span>{reviewedRoles.size}/5 roles covered</span></header>
    <p className="form-note">Missing roles are intentionally blank until a reviewer records an evidence-linked view.</p>
    <div className="runtime-review-coverage">{roles.map(([value, label]) => <span key={value} className={reviewedRoles.has(value) ? "review-role covered" : "review-role"}>{label}: {reviewedRoles.has(value) ? "recorded" : "not reviewed"}</span>)}</div>
    <form onSubmit={submit}>
      <div className="red-team-grid">
        <label htmlFor="runtime-ic-role">Review lens<select id="runtime-ic-role" className="text-control" value={role} onChange={(event) => setRole(event.target.value as InvestmentCommitteeReviewInput["role"])}>{roles.map(([value, label]) => <option value={value} key={value}>{label}</option>)}</select></label>
        <label htmlFor="runtime-ic-reviewer">Reviewer<input id="runtime-ic-reviewer" className="text-control" value={reviewer} onChange={(event) => setReviewer(event.target.value)} required /></label>
        <label htmlFor="runtime-ic-position">Position<select id="runtime-ic-position" className="text-control" value={position} onChange={(event) => setPosition(event.target.value as InvestmentCommitteeReviewInput["position"])} required><option value="SUPPORTIVE">Supportive</option><option value="CHALLENGING">Challenging</option><option value="MIXED">Mixed</option><option value="INSUFFICIENT">Insufficient evidence</option></select></label>
        <label htmlFor="runtime-ic-recommendation">Recommendation<select id="runtime-ic-recommendation" className="text-control" value={recommendation} onChange={(event) => setRecommendation(event.target.value as InvestmentCommitteeReviewInput["recommendation"])} required><option value="APPROVE">Approve</option><option value="HOLD">Hold</option><option value="REJECT">Reject</option><option value="REQUEST_RESEARCH">Request research</option></select></label>
        <label htmlFor="runtime-ic-evidence">Evidence<select id="runtime-ic-evidence" className="text-control red-team-evidence-select" multiple size={Math.min(5, Math.max(2, run.evidence.length))} value={evidenceIds} onChange={(event) => setEvidenceIds(Array.from(event.target.selectedOptions, (option) => option.value))} required>{run.evidence.map((item) => <option key={item.id} value={item.id}>{item.source_title ?? item.id} · {item.qualification}</option>)}</select><small>Select the records considered by this reviewer; their original qualification is retained.</small></label>
        <label htmlFor="runtime-ic-rationale">Rationale<textarea id="runtime-ic-rationale" className="text-control" rows={4} value={rationale} onChange={(event) => setRationale(event.target.value)} placeholder="Explain the view, key assumption, and what would change it." required /></label>
      </div>
      {mutation.isError && <p className="form-error" role="alert">{mutation.error.message}</p>}
      {mutation.isSuccess && <p className="form-success" role="status">IC review saved to this run.</p>}
      <div className="form-actions"><button type="submit" className="blue-button" disabled={!canSubmit || mutation.isPending}>{mutation.isPending ? "Saving review…" : "Save IC review"}</button></div>
    </form>
  </section>;
}
