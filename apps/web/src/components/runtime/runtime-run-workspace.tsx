"use client";

import { useState } from "react";
import { AppShell } from "@/components/shell/app-shell";
import { useCancelRuntimeRunMutation, useExecuteRuntimeRunMutation, useRuntimeRunQuery } from "@/queries/use-runtime-run";

export function RuntimeRunWorkspace({ runId }: { runId: string }) {
  const query = useRuntimeRunQuery(runId);
  const execute = useExecuteRuntimeRunMutation(runId);
  const cancel = useCancelRuntimeRunMutation(runId);
  const [reason, setReason] = useState("Analyst stopped the run.");

  if (query.isPending) return <AppShell context={<div />}><div className="skeleton-stack"><i /><i /><i /></div></AppShell>;
  if (query.isError) return <AppShell context={<div />}><div className="error-state" role="alert"><b>Runtime run could not be loaded</b><span>{query.error.message}</span><button type="button" onClick={() => query.refetch()}>Retry</button></div></AppShell>;

  const run = query.data;
  const terminal = ["COMPLETED", "PARTIAL", "FAILED", "CANCELLED"].includes(run.state);
  const qualified = run.evidence.filter((item) => item.qualification === "QUALIFIED").length;
  const needsReview = run.evidence.filter((item) => item.qualification === "NEEDS_REVIEW").length;
  const counter = run.evidence.filter((item) => item.stance === "COUNTER" || item.stance === "CONFLICTING").length;

  return (
    <AppShell context={<><div className="context-heading"><b>Runtime run</b><span>{run.state}</span></div><div className="context-summary"><small>TASKS</small><b>{run.tasks.length}</b><small>EVIDENCE</small><b>{run.evidence.length}</b><small>MEMO</small><b>{run.memo?.status ?? "pending"}</b></div></>}>
      <div className="page-title"><div><p>LIVE RUNTIME · {run.id}</p><h1>Research execution</h1><span>Backend-driven state, evidence coverage, and review-gated output.</span></div><span className={`thesis-state ${run.state.toLowerCase()}`}>{run.state}</span></div>
      <section className="decision-panel">
        <header><div><small>RUN CONTROL</small><h2>Execution state</h2></div><div className="form-actions compact"><button type="button" className="outline" onClick={() => query.refetch()}>Refresh</button>{run.state === "CREATED" && <button type="button" className="blue-button" disabled={execute.isPending} onClick={() => execute.mutate()}>{execute.isPending ? "Executing…" : "Start research"}</button>}</div></header>
        {!terminal && <div className="form-actions"><input className="text-control" value={reason} onChange={(event) => setReason(event.target.value)} aria-label="Cancellation reason" /><button type="button" className="outline" disabled={cancel.isPending || reason.trim().length < 3} onClick={() => cancel.mutate(reason)}>{cancel.isPending ? "Cancelling…" : "Cancel run"}</button></div>}
        {(execute.isError || cancel.isError) && <p className="form-error" role="alert">{(execute.error ?? cancel.error)?.message}</p>}
      </section>
      <section className="decision-panel"><header><div><small>TASK CONTRACT</small><h2>Research tasks</h2></div><span>{run.tasks.filter((task) => task.state === "COMPLETED").length} / {run.tasks.length} completed</span></header><div className="runtime-task-list">{run.tasks.map((task) => <article className="runtime-task" key={task.id}><b>{task.title}</b><span>{task.id}</span><em>{task.state}</em></article>)}</div></section>
      <section className="company-section-grid"><article className="company-section"><header><h3>Evidence coverage</h3><span>{run.evidence.length} observed</span></header><p>{qualified} qualified · {needsReview} needs review · {counter} counter/conflicting</p></article><article className="company-section"><header><h3>Memo projection</h3><span>{run.memo?.status ?? "not generated"}</span></header><p>{run.memo?.executive_summary ?? "Memo is generated after synthesis."}</p></article></section>
      {run.memo && <section className="decision-panel"><header><div><small>REVIEW ARTIFACT</small><h2>{run.memo.title}</h2></div><span>{run.memo.evidence_ids.length} linked evidence</span></header><p>{run.memo.executive_summary}</p><p>Counter/conflicting evidence: {run.memo.counter_evidence_ids.length} · unresolved requirements: {run.memo.unresolved_requirement_ids.length}</p><div className="memo-section-grid">{run.memo.sections.map((section) => <article className="memo-section" key={section.section_key}><header><h3>{section.title}</h3><span>{section.evidence_ids.length} evidence</span></header><p>{section.body}</p><small>{section.claim_ids.length} claims · {section.unresolved_requirement_ids.length} unresolved</small></article>)}</div></section>}
    </AppShell>
  );
}
