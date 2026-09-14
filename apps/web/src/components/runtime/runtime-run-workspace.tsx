"use client";

import { useRouter } from "next/navigation";
import { useState } from "react";
import { AppShell } from "@/components/shell/app-shell";
import { FinancialAnalysisForm } from "@/components/runtime/financial-analysis-form";
import { RedTeamReviewForm } from "@/components/runtime/red-team-review-form";
import { RuntimeDecisionForm } from "@/components/runtime/runtime-decision-form";
import { RuntimeEvidenceTrace } from "@/components/runtime/runtime-evidence-trace";
import { RuntimeClaimTrace } from "@/components/runtime/runtime-claim-trace";
import { RuntimeCalculationLedger } from "@/components/runtime/runtime-calculation-ledger";
import { RuntimePlanContext } from "@/components/runtime/runtime-plan-context";
import { RuntimeTaskContract } from "@/components/runtime/runtime-task-contract";
import { RuntimeToolTrace } from "@/components/runtime/runtime-tool-trace";
import { RuntimeValuationScenarios } from "@/components/runtime/runtime-valuation-scenarios";
import { ValuationScenarioForm } from "@/components/runtime/valuation-scenario-form";
import { RuntimeCaseHistory } from "@/components/runtime/runtime-case-history";
import { RuntimeEvaluation } from "@/components/runtime/runtime-evaluation";
import { RuntimeMemoExport } from "@/components/runtime/runtime-memo-export";
import { RuntimeIcReview } from "@/components/runtime/runtime-ic-review";
import { useCancelRuntimeRunMutation, useCreateRuntimeRerunMutation, useExecuteRuntimeRunMutation, useReplanRuntimeRunMutation, useRuntimeCaseRunsQuery, useRuntimeEvaluationQuery, useRuntimeMemoryQuery, useRuntimeRunQuery, useRuntimeTraceQuery } from "@/queries/use-runtime-run";

export function RuntimeRunWorkspace({ runId }: { runId: string }) {
  const router = useRouter();
  const query = useRuntimeRunQuery(runId);
  const caseRunsQuery = useRuntimeCaseRunsQuery(query.data?.case_id ?? "");
  const evaluationQuery = useRuntimeEvaluationQuery(runId);
  const rerun = useCreateRuntimeRerunMutation(query.data?.case_id ?? "");
  const memoryQuery = useRuntimeMemoryQuery(runId, Boolean(query.data?.memo));
  const traceQuery = useRuntimeTraceQuery(runId);
  const execute = useExecuteRuntimeRunMutation(runId);
  const replan = useReplanRuntimeRunMutation(runId);
  const cancel = useCancelRuntimeRunMutation(runId);
  const [reason, setReason] = useState("Analyst stopped the run.");

  if (query.isPending) return <AppShell context={<div />}><div className="skeleton-stack"><i /><i /><i /></div></AppShell>;
  if (query.isError) return <AppShell context={<div />}><div className="error-state" role="alert"><b>Runtime run could not be loaded</b><span>{query.error.message}</span><button type="button" onClick={() => query.refetch()}>Retry</button></div></AppShell>;

  const run = query.data;
  const terminal = ["COMPLETED", "PARTIAL", "FAILED", "CANCELLED", "BLOCKED"].includes(run.state);
  const qualified = run.evidence.filter((item) => item.qualification === "QUALIFIED").length;
  const needsReview = run.evidence.filter((item) => item.qualification === "NEEDS_REVIEW").length;
  const counter = run.evidence.filter((item) => item.stance === "COUNTER" || item.stance === "CONFLICTING").length;
  function createRerun() {
    void rerun.mutateAsync().then((result) => router.push(`/runtime/${encodeURIComponent(result.run_id)}`), () => undefined);
  }

  return (
    <AppShell context={<><div className="context-heading"><b>Runtime run</b><span>{run.state}</span></div><div className="context-summary"><small>TASKS</small><b>{run.tasks.length}</b><small>EVIDENCE</small><b>{run.evidence.length}</b><small>MEMO</small><b>{run.memo?.status ?? "pending"}</b></div></>}>
      <div className="page-title"><div><p>LIVE RUNTIME · {run.id}</p><h1>Research execution</h1><span>Backend-driven state, evidence coverage, and review-gated output.</span></div><span className={`thesis-state ${run.state.toLowerCase()}`}>{run.state}</span></div>
      <section className="decision-panel">
        <header><div><small>RUN CONTROL</small><h2>Execution state</h2></div><div className="form-actions compact"><button type="button" className="outline" onClick={() => query.refetch()}>Refresh</button>{run.state === "CREATED" && <button type="button" className="blue-button" disabled={execute.isPending} onClick={() => execute.mutate()}>{execute.isPending ? "Executing…" : "Start research"}</button>}{run.state === "PARTIAL" && <button type="button" className="blue-button" disabled={replan.isPending} onClick={() => replan.mutate()}>{replan.isPending ? "Replanning…" : "Replan missing evidence"}</button>}</div></header>
        {!terminal && <p className="form-note" role="status">Live refresh every 2 seconds while this run is active.</p>}
        {!terminal && <div className="form-actions"><input className="text-control" value={reason} onChange={(event) => setReason(event.target.value)} aria-label="Cancellation reason" /><button type="button" className="outline" disabled={cancel.isPending || reason.trim().length < 3} onClick={() => cancel.mutate(reason)}>{cancel.isPending ? "Cancelling…" : "Cancel run"}</button></div>}
        {(execute.isError || cancel.isError || replan.isError) && <p className="form-error" role="alert">{(execute.error ?? cancel.error ?? replan.error)?.message}</p>}
      </section>
      <RuntimePlanContext plan={run.plan} />
      <RuntimeEvaluation evaluation={evaluationQuery.data} isPending={evaluationQuery.isPending} error={evaluationQuery.error} />
      <RuntimeCaseHistory runs={caseRunsQuery.data} activeRunId={run.id} isPending={caseRunsQuery.isPending} error={caseRunsQuery.error} onCreateRerun={createRerun} isRerunPending={rerun.isPending} rerunError={rerun.error} />
      <RuntimeTaskContract tasks={run.tasks} traceTasks={traceQuery.data?.tasks} />
      <RuntimeToolTrace executions={run.tool_executions} />
      <RuntimeEvidenceTrace evidence={run.evidence} />
      <RuntimeClaimTrace claims={run.claims} evidence={run.evidence} />
      <section className="company-section-grid"><article className="company-section"><header><h3>Evidence coverage</h3><span>{run.evidence.length} observed</span></header><p>{qualified} qualified · {needsReview} needs review · {counter} counter/conflicting</p></article><article className="company-section"><header><h3>Memo projection</h3><span>{run.memo?.status ?? "not generated"}</span></header><p>{run.memo?.executive_summary ?? "Memo is generated after synthesis."}</p></article></section>
      {run.valuation_scenarios && <RuntimeValuationScenarios artifact={run.valuation_scenarios} />}
      {qualified > 0 && !["FAILED", "CANCELLED", "BLOCKED"].includes(run.state) && <ValuationScenarioForm run={run} />}
      {qualified > 0 && !["FAILED", "CANCELLED", "BLOCKED"].includes(run.state) && <FinancialAnalysisForm run={run} />}
      {run.financial_analysis && <><section className="decision-panel"><header><div><small>CALCULATION ARTIFACT · EXPLICIT INPUTS</small><h2>Financial analysis · {run.financial_analysis.period}</h2></div><span>{Object.values(run.financial_analysis.evidence_ids).flat().length} linked evidence</span></header><div className="company-section-grid"><article className="company-section"><header><h3>Revenue growth</h3></header><p>{run.financial_analysis.revenue_growth_pct ?? "Unavailable"}</p></article><article className="company-section"><header><h3>Free cash flow</h3></header><p>{run.financial_analysis.free_cash_flow ?? "Unavailable"}</p></article><article className="company-section"><header><h3>Net cash</h3></header><p>{run.financial_analysis.net_cash ?? "Unavailable"}</p></article></div><small>Values were supplied explicitly and linked to qualified evidence; unavailable metrics are not inferred.</small></section><RuntimeCalculationLedger entries={run.financial_analysis.calculation_ledger} /></>}
      {!terminal && <RedTeamReviewForm run={run} />}
      {run.red_team_reviews.length > 0 && <section className="decision-panel"><header><div><small>RED-TEAM REVIEW · THESIS CHALLENGES</small><h2>Disconfirming review</h2></div><span>{run.red_team_reviews.length} reviews</span></header>{run.red_team_reviews.map((review) => <article className="memo-section" key={review.id}><header><h3>{review.outcome}</h3><span>{review.reviewer} · {review.evidence_ids.length} evidence</span></header><p>{review.challenge}</p><small>{review.rationale}</small></article>)}</section>}
      {run.thesis && !["FAILED", "CANCELLED", "BLOCKED"].includes(run.state) && <RuntimeIcReview run={run} />}
      {run.thesis && !["FAILED", "CANCELLED", "BLOCKED"].includes(run.state) && <RuntimeDecisionForm run={run} />}
      {run.decisions.length > 0 && <section className="decision-panel"><header><div><small>DECISION LOG · APPEND-ONLY</small><h2>Human decisions</h2></div><span>{run.decisions.length} recorded</span></header><div className="runtime-decision-history">{run.decisions.map((decision) => <article className="memo-section" key={decision.id}><header><h3>{decision.action.replaceAll("_", " ")}</h3><span>{decision.actor} · {new Date(decision.created_at).toLocaleString()}</span></header><p>{decision.rationale}</p><small>Target thesis: {decision.target_id}</small></article>)}</div></section>}
      {run.memo && <section className="decision-panel"><header><div><small>REVIEW ARTIFACT</small><h2>{run.memo.title}</h2></div><div className="form-actions compact"><span>{run.memo.evidence_ids.length} linked evidence · {run.memo.red_team_review_ids.length} Red-team reviews · {run.memo.ic_review_ids.length} IC reviews</span><RuntimeMemoExport run={run} /></div></header><p>{run.memo.executive_summary}</p><p>Counter/conflicting evidence: {run.memo.counter_evidence_ids.length} · unresolved requirements: {run.memo.unresolved_requirement_ids.length}</p><div className="memo-section-grid">{run.memo.sections.map((section) => <article className="memo-section" key={section.section_key}><header><h3>{section.title}</h3><span>{section.evidence_ids.length} evidence</span></header><p>{section.body}</p><small>{section.claim_ids.length} claims · {section.unresolved_requirement_ids.length} unresolved</small></article>)}</div></section>}
      {run.memo && memoryQuery.data && <section className="decision-panel"><header><div><small>INVESTMENT MEMORY · OBSERVED HISTORY</small><h2>{memoryQuery.data.target}</h2></div><span>{memoryQuery.data.run_ids.length} runs</span></header><p>Latest thesis: {memoryQuery.data.latest_thesis_id}</p><p>{memoryQuery.data.latest_thesis_delta?.summary ?? "First recorded target run; no prior thesis delta exists."}</p><small>Memory is an auditable history projection, not confidence or investment advice.</small></section>}
    </AppShell>
  );
}
