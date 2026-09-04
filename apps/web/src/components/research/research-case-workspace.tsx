"use client";

import { AlertTriangle, Check, ChevronDown, ChevronRight, Circle, Pause, Play, RefreshCw, Save, Search, ShieldAlert, Trash2 } from "lucide-react";
import Link from "next/link";
import { useEffect, useState } from "react";
import { AppShell } from "@/components/shell/app-shell";
import type { ResearchCaseWorkspace as Workspace, ResearchFinding, ResearchPlan, ResearchRun } from "@/domain/research";
import { useResearchCaseQuery, useResearchRunControlMutation, useUpdateFindingMutation, useUpdateResearchPlanMutation } from "@/queries/use-research-case";
import { getVisibleFindingIds } from "@/features/research/research-progress";

export function ResearchCaseWorkspace({ caseId }: { caseId: string }) {
  const researchCase = useResearchCaseQuery(caseId);
  const updatePlan = useUpdateResearchPlanMutation(caseId);
  const controlRun = useResearchRunControlMutation(caseId);
  const updateFinding = useUpdateFindingMutation(caseId);
  const [eventIndex, setEventIndex] = useState(-1);
  const [expandedFinding, setExpandedFinding] = useState<string | null>(null);
  const [localPlan, setLocalPlan] = useState<ResearchPlan | null>(null);

  const data = researchCase.data;
  useEffect(() => {
    if (!data || data.run.status !== "running" || eventIndex < 0) return;
    if (eventIndex >= data.timeline.length - 1) {
      const timeout = window.setTimeout(() => controlRun.mutate("complete"), 700);
      return () => window.clearTimeout(timeout);
    }
    const timeout = window.setTimeout(() => setEventIndex((current) => current + 1), 850);
    return () => window.clearTimeout(timeout);
  }, [controlRun, data, eventIndex]);

  if (researchCase.isPending) return <AppShell context={<CaseContextSkeleton />}><div className="skeleton-stack"><i /><i /><i /></div></AppShell>;
  if (researchCase.isError) return <AppShell context={<CaseContextSkeleton />}><div className="error-state" role="alert"><b>Research Case could not be loaded</b><span>{researchCase.error.message}</span><button type="button" onClick={() => researchCase.refetch()}>Try again</button></div></AppShell>;
  if (!data) return null;
  const editablePlan = localPlan ?? data.plan;

  const visibleEventIndex = data.run.status === "completed" ? data.timeline.length - 1 : eventIndex;
  const currentStage = visibleEventIndex >= 0 ? data.timeline[visibleEventIndex]?.stage ?? "planning" : data.run.stage;
  const visibleFindingIds = getVisibleFindingIds(data.findings, currentStage);
  const visibleFindings = data.findings.filter((finding) => visibleFindingIds.includes(finding.id));

  async function run(action: "start" | "cancel" | "restart") {
    if (action !== "cancel") setEventIndex(0);
    await controlRun.mutateAsync(action);
  }

  return <AppShell context={<CaseContext data={data} currentStage={currentStage} visibleFindings={visibleFindings.length} />}>
    <header className="case-header"><div><p>RESEARCH CASE · DEEP RESEARCH</p><h1>{data.case.question}</h1><div className="case-meta"><Status status={data.run.status} /><span>Updated 2m ago</span><span>Evidence coverage <b>{data.evidenceCoverage}%</b></span><small>{data.fixtureNotice}</small></div></div><div className="case-actions">{data.run.status === "running" ? <button className="outline" type="button" onClick={() => run("cancel")}><Pause size={15} />Cancel run</button> : <button className="blue-button" type="button" onClick={() => run(data.run.status === "cancelled" || data.run.status === "completed" ? "restart" : "start")}><Play size={15} />{data.run.status === "queued" ? "Start research" : "Restart research"}</button>}</div></header>
    <section className="case-goal"><small>RESEARCH GOAL</small><p>{data.researchGoal}</p></section>
    <div className="case-grid">
      <section className="case-panel plan-panel"><header><div><small>01 · RESEARCH PLAN</small><h2>Questions and priority</h2></div><button className="outline" type="button" disabled={!updatePlan.isPending && JSON.stringify(editablePlan) === JSON.stringify(data.plan)} onClick={() => updatePlan.mutate(editablePlan)}><Save size={14} />{updatePlan.isPending ? "Saving…" : "Save plan"}</button></header>{editablePlan.sections.map((section) => <div className="case-plan-section" key={section.id}><h3>{section.title}<span>{section.tasks.length}</span></h3>{section.tasks.map((task, index) => <div className="case-plan-task" key={task.id}><button type="button" className={`task-state ${task.status}`} title="Cycle task status" aria-label={`Change status for ${task.question}`} onClick={() => setLocalPlan(cycleTask(editablePlan, section.id, task.id))}>{task.status === "completed" ? <Check size={13} /> : task.status === "needs-review" ? <AlertTriangle size={13} /> : <Circle size={12} />}</button><input value={task.question} onChange={(event) => setLocalPlan(changeQuestion(editablePlan, section.id, task.id, event.target.value))} aria-label={`${section.title} research question ${index + 1}`} /><select value={task.priority} aria-label={`Priority for ${task.question}`} onChange={(event) => setLocalPlan(changePriority(editablePlan, section.id, task.id, Number(event.target.value)))}>{Array.from({ length: 10 }, (_, value) => <option key={value + 1} value={value + 1}>P{value + 1}</option>)}</select><button type="button" aria-label={`Delete ${task.question}`} disabled={section.tasks.length === 1} onClick={() => setLocalPlan(removeTask(editablePlan, section.id, task.id))}><Trash2 size={13} /></button><button type="button" className="rerun-task" onClick={() => setLocalPlan(setTaskRunning(editablePlan, section.id, task.id))}><RefreshCw size={13} />Rerun</button></div>)}</div>)}</section>
      <section className="case-panel execution-panel"><header><div><small>02 · STREAMING RESEARCH</small><h2>{data.run.status === "queued" ? "Ready to research" : data.run.status === "cancelled" ? "Research cancelled" : data.run.status === "completed" ? "Research pass complete" : data.timeline[Math.max(0, visibleEventIndex)]?.label}</h2></div><Status status={data.run.status} /></header><div className="research-timeline">{data.timeline.map((event, index) => { const state = data.run.status === "completed" || index < visibleEventIndex ? "complete" : index === visibleEventIndex ? "active" : "pending"; return <div className={`timeline-event ${state}`} key={event.id}><i>{state === "complete" ? <Check size={12} /> : state === "active" ? <Search size={12} /> : <Circle size={10} />}</i><div><b>{event.label}</b><span>{event.detail}</span></div></div>; })}</div></section>
    </div>
    <section className="findings-section"><header><div><small>03 · RESEARCH FINDINGS</small><h2>Structured findings before prose</h2></div><span>{visibleFindings.length} of {data.findings.length} revealed</span></header>{visibleFindings.length === 0 ? <div className="empty-state"><b>Findings appear as evidence is extracted</b><span>Start the mock research run to watch findings emerge from staged source work.</span></div> : <div className="finding-list">{visibleFindings.map((finding) => <FindingRow finding={finding} expanded={expandedFinding === finding.id} onToggle={() => setExpandedFinding(expandedFinding === finding.id ? null : finding.id)} onSave={(summary) => updateFinding.mutate({ ...finding, summary })} key={finding.id} />)}</div>}</section>
  </AppShell>;
}

function FindingRow({ finding, expanded, onToggle, onSave }: { finding: ResearchFinding; expanded: boolean; onToggle: () => void; onSave: (summary: string) => void }) { const [summary, setSummary] = useState(finding.summary); return <article className="finding-row"><button type="button" onClick={onToggle} aria-expanded={expanded}><span className={`confidence ${finding.confidence}`}>{finding.confidence === "needs-review" ? "Needs review" : `${finding.confidence} confidence`}</span><div><h3>{finding.title}</h3><p>{finding.summary}</p></div><div className="finding-counts"><span><b>{finding.supportingEvidenceCount}</b> supporting</span><span className="counter"><b>{finding.counterEvidenceCount}</b> counter</span></div>{expanded ? <ChevronDown size={16} /> : <ChevronRight size={16} />}</button>{expanded && <div className="finding-detail"><b>Analyst-editable finding</b><textarea value={summary} rows={3} onChange={(event) => setSummary(event.target.value)} aria-label={`Edit ${finding.title}`} /><button className="outline" type="button" disabled={summary.trim().length < 5 || summary === finding.summary} onClick={() => onSave(summary)}>Save finding edit</button><b>Supporting signals</b><ul>{finding.supportingSignals.map((signal) => <li key={signal}>{signal}</li>)}</ul><Link href="/evidence" className="link-button">Inspect evidence and counter-evidence</Link></div>}</article>; }
function Status({ status }: { status: ResearchRun["status"] }) { const label = status === "awaiting-review" ? "Awaiting review" : status[0].toUpperCase() + status.slice(1); return <span className={`run-status ${status}`}>{status === "failed" || status === "cancelled" ? <ShieldAlert size={12} /> : <i />}{label}</span>; }
function CaseContext({ data, currentStage, visibleFindings }: { data: Workspace; currentStage: string; visibleFindings: number }) { return <><div className="context-heading"><b>Run intelligence</b><span>Mock execution</span></div><div className="context-summary"><small>CURRENT STAGE</small><b>{currentStage.replace("-", " ")}</b><small>PLAN TASKS</small><b>{data.plan.sections.reduce((total, section) => total + section.tasks.length, 0)}</b><small>VISIBLE FINDINGS</small><b>{visibleFindings}</b><small>EVIDENCE COVERAGE</small><b>{data.evidenceCoverage}%</b><small>OPEN QUESTION</small><b>{data.case.openQuestion}</b></div><p className="context-note">Streaming stages are simulated fixture events. Findings remain traceable to supporting and counter-evidence.</p></>; }
function CaseContextSkeleton() { return <div className="skeleton-stack compact"><i /><i /><i /></div>; }

const nextStatuses = { pending: "running", running: "completed", completed: "needs-review", "needs-review": "pending" } as const;
function cycleTask(plan: ResearchPlan, sectionId: string, taskId: string): ResearchPlan { return { ...plan, sections: plan.sections.map((section) => section.id === sectionId ? { ...section, tasks: section.tasks.map((task) => task.id === taskId ? { ...task, status: nextStatuses[task.status] } : task) } : section) }; }
function changeQuestion(plan: ResearchPlan, sectionId: string, taskId: string, question: string): ResearchPlan { return { ...plan, sections: plan.sections.map((section) => section.id === sectionId ? { ...section, tasks: section.tasks.map((task) => task.id === taskId ? { ...task, question } : task) } : section) }; }
function changePriority(plan: ResearchPlan, sectionId: string, taskId: string, priority: number): ResearchPlan { return { ...plan, sections: plan.sections.map((section) => section.id === sectionId ? { ...section, tasks: section.tasks.map((task) => task.id === taskId ? { ...task, priority } : task).sort((a, b) => a.priority - b.priority) } : section) }; }
function removeTask(plan: ResearchPlan, sectionId: string, taskId: string): ResearchPlan { return { ...plan, sections: plan.sections.map((section) => section.id === sectionId ? { ...section, tasks: section.tasks.filter((task) => task.id !== taskId) } : section) }; }
function setTaskRunning(plan: ResearchPlan, sectionId: string, taskId: string): ResearchPlan { return { ...plan, sections: plan.sections.map((section) => section.id === sectionId ? { ...section, tasks: section.tasks.map((task) => task.id === taskId ? { ...task, status: "running" } : task) } : section) }; }
