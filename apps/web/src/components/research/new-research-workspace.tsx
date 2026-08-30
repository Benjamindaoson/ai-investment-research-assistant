"use client";

import { ArrowDown, ArrowLeft, ArrowUp, FilePlus2, Plus, Trash2 } from "lucide-react";
import { useRouter } from "next/navigation";
import { useMemo, useState } from "react";
import { AppShell } from "@/components/shell/app-shell";
import {
  researchSetupSchema,
  type ResearchPlan,
  type ResearchScope,
  type ResearchSetup,
  type ResearchSourceType,
} from "@/domain/research";
import {
  useCreateResearchCaseMutation,
  useProposeResearchPlanMutation,
  useResearchSetupOptionsQuery,
} from "@/queries/use-research-setup";

const sourceLabels: Record<ResearchSourceType, string> = {
  official: "Official",
  "research-papers": "Research papers",
  news: "News",
  github: "GitHub",
  patents: "Patents",
  hiring: "Hiring",
  "uploaded-documents": "Uploaded documents",
};

const defaultQuestion = "未来三年具身智能产业最大的价值池在哪里？";

export function NewResearchWorkspace({ initialQuestion = defaultQuestion }: { initialQuestion?: string }) {
  const router = useRouter();
  const options = useResearchSetupOptionsQuery();
  const proposePlan = useProposeResearchPlanMutation();
  const createCase = useCreateResearchCaseMutation();
  const [step, setStep] = useState<"setup" | "plan">("setup");
  const [question, setQuestion] = useState(initialQuestion);
  const [scope, setScope] = useState<ResearchScope>("deep");
  const [targetIds, setTargetIds] = useState<string[]>(["industry-embodied", "technology-robot-data"]);
  const [timeRange, setTimeRange] = useState<ResearchSetup["timeRange"]>("3-years");
  const [customTimeRange, setCustomTimeRange] = useState("");
  const [sourceTypes, setSourceTypes] = useState<ResearchSourceType[]>(["official", "research-papers", "news", "patents", "hiring"]);
  const [attachments, setAttachments] = useState<string[]>([]);
  const [plan, setPlan] = useState<ResearchPlan | null>(null);
  const [error, setError] = useState("");

  const setup = useMemo(() => ({ question, scope, targetIds, timeRange, customTimeRange, sourceTypes, attachmentNames: attachments }), [question, scope, targetIds, timeRange, customTimeRange, sourceTypes, attachments]);

  async function continueToPlan() {
    const parsed = researchSetupSchema.safeParse(setup);
    if (!parsed.success) {
      setError(parsed.error.issues[0]?.message ?? "Review the research setup.");
      return;
    }
    setError("");
    const nextPlan = await proposePlan.mutateAsync(parsed.data);
    setPlan(nextPlan);
    setStep("plan");
  }

  async function startResearch() {
    const parsed = researchSetupSchema.safeParse(setup);
    if (!parsed.success || !plan) return;
    const result = await createCase.mutateAsync({ setup: parsed.data, plan });
    router.push(`/research/${result.caseId}`);
  }

  const context = <SetupContext step={step} setup={setup} targetCount={targetIds.length} taskCount={plan?.sections.reduce((total, section) => total + section.tasks.length, 0) ?? 0} />;
  if (options.isPending) return <AppShell context={context}><div className="skeleton-stack"><i /><i /><i /></div></AppShell>;
  if (options.isError) return <AppShell context={context}><div className="error-state" role="alert"><b>Research setup could not be loaded</b><span>{options.error.message}</span><button type="button" onClick={() => options.refetch()}>Try again</button></div></AppShell>;

  return (
    <AppShell context={context}>
      <div className="page-title research-create-title"><div><p>NEW RESEARCH · {step === "setup" ? "SETUP" : "PLAN REVIEW"}</p><h1>{step === "setup" ? "Frame the research" : "Review the research plan"}</h1><span>{step === "setup" ? "Set boundaries before the mock research worker begins." : "Shape the questions before evidence collection starts."}</span><small className="fixture-notice">{options.data.fixtureNotice}</small></div></div>
      {step === "setup" ? (
        <div className="setup-stack">
          <Section title="Research question" description="The original question remains attached to the case and all later findings."><textarea value={question} onChange={(event) => setQuestion(event.target.value)} aria-label="Research question" rows={3} /></Section>
          <Section title="Research scope" description="Quick is narrower; Deep expands counter-evidence and source coverage."><div className="choice-grid two">{(["quick", "deep"] as const).map((item) => <Choice key={item} selected={scope === item} onClick={() => setScope(item)} title={item === "quick" ? "Quick Research" : "Deep Research"} detail={item === "quick" ? "Focused scan · fewer branches" : "Full plan · explicit counter-evidence"} />)}</div></Section>
          <Section title="Targets" description="Select at least one company, technology, or industry."><div className="target-grid">{options.data.targets.map((target) => <button type="button" key={target.id} className={targetIds.includes(target.id) ? "target-chip selected" : "target-chip"} aria-pressed={targetIds.includes(target.id)} onClick={() => setTargetIds(toggle(targetIds, target.id))}><small>{target.kind}</small>{target.label}</button>)}</div></Section>
          <Section title="Time range" description="Choose the horizon used to assess evidence and catalysts."><div className="choice-grid three">{(["12-months", "3-years", "custom"] as const).map((item) => <Choice key={item} selected={timeRange === item} onClick={() => setTimeRange(item)} title={item === "12-months" ? "12 months" : item === "3-years" ? "3 years" : "Custom"} detail={item === "custom" ? "Define a specific horizon" : "Relative to the demo date"} />)}</div>{timeRange === "custom" && <input className="text-control" value={customTimeRange} onChange={(event) => setCustomTimeRange(event.target.value)} placeholder="e.g. Jan 2025 through Dec 2028" aria-label="Custom time range" />}</Section>
          <Section title="Sources" description="The plan will preserve source type and citation provenance."><div className="source-grid">{options.data.recommendedSourceTypes.map((source) => <label key={source}><input type="checkbox" checked={sourceTypes.includes(source)} onChange={() => setSourceTypes(toggle(sourceTypes, source))} />{sourceLabels[source]}</label>)}</div></Section>
          <Section title="Uploaded documents" description="Attachments are mock local state in this frontend-only phase."><label className="file-control"><FilePlus2 size={17} />Add files<input type="file" multiple onChange={(event) => setAttachments([...attachments, ...Array.from(event.target.files ?? []).map((file) => file.name)])} /></label>{attachments.map((name) => <div className="attachment" key={name}><span>{name}</span><button type="button" aria-label={`Remove ${name}`} onClick={() => setAttachments(attachments.filter((item) => item !== name))}><Trash2 size={15} /></button></div>)}</Section>
          {error && <p className="form-error" role="alert">{error}</p>}
          <div className="form-actions"><button type="button" className="outline" onClick={() => router.push("/")}>Cancel</button><button type="button" className="blue-button" disabled={proposePlan.isPending} onClick={continueToPlan}>{proposePlan.isPending ? "Generating mock plan…" : "Continue to research plan"}</button></div>
        </div>
      ) : plan ? <PlanEditor plan={plan} onChange={setPlan} onBack={() => setStep("setup")} onStart={startResearch} pending={createCase.isPending} /> : null}
    </AppShell>
  );
}

function Section({ title, description, children }: { title: string; description: string; children: React.ReactNode }) { return <section className="setup-section"><header><h2>{title}</h2><p>{description}</p></header><div>{children}</div></section>; }
function Choice({ selected, onClick, title, detail }: { selected: boolean; onClick: () => void; title: string; detail: string }) { return <button type="button" className={selected ? "choice selected" : "choice"} aria-pressed={selected} onClick={onClick}><b>{title}</b><span>{detail}</span></button>; }
function toggle<T>(items: T[], item: T) { return items.includes(item) ? items.filter((value) => value !== item) : [...items, item]; }

function PlanEditor({ plan, onChange, onBack, onStart, pending }: { plan: ResearchPlan; onChange: (plan: ResearchPlan) => void; onBack: () => void; onStart: () => void; pending: boolean }) {
  function updateTasks(sectionId: string, tasks: ResearchPlan["sections"][number]["tasks"]) { onChange({ ...plan, sections: plan.sections.map((section) => section.id === sectionId ? { ...section, tasks } : section) }); }
  return <div className="plan-editor"><section className="research-goal"><small>STRUCTURED RESEARCH GOAL</small><textarea value={plan.goal} rows={3} onChange={(event) => onChange({ ...plan, goal: event.target.value })} aria-label="Research goal" /></section>{plan.sections.map((section) => <section className="plan-section" key={section.id}><header><div><small>RESEARCH LENS</small><h2>{section.title}</h2></div><button type="button" className="outline" onClick={() => updateTasks(section.id, [...section.tasks, { id: `${section.id}-task-${Date.now()}`, question: "New research question", priority: section.tasks.length + 1, status: "pending" }])}><Plus size={14} />Add question</button></header>{section.tasks.map((task, index) => <div className="plan-task" key={task.id}><span>{task.priority}</span><input value={task.question} aria-label={`${section.title} question ${index + 1}`} onChange={(event) => updateTasks(section.id, section.tasks.map((item) => item.id === task.id ? { ...item, question: event.target.value } : item))} /><div><button type="button" disabled={index === 0} aria-label="Move question up" onClick={() => updateTasks(section.id, move(section.tasks, index, index - 1))}><ArrowUp size={14} /></button><button type="button" disabled={index === section.tasks.length - 1} aria-label="Move question down" onClick={() => updateTasks(section.id, move(section.tasks, index, index + 1))}><ArrowDown size={14} /></button><button type="button" disabled={section.tasks.length === 1} aria-label="Delete question" onClick={() => updateTasks(section.id, section.tasks.filter((item) => item.id !== task.id))}><Trash2 size={14} /></button></div></div>)}</section>)}<div className="form-actions"><button type="button" className="outline back-action" onClick={onBack}><ArrowLeft size={15} />Back to setup</button><button type="button" className="blue-button" disabled={pending} onClick={onStart}>{pending ? "Creating mock research…" : "Start Research"}</button></div></div>;
}

function move<T>(items: T[], from: number, to: number) { const next = [...items]; const [item] = next.splice(from, 1); if (item !== undefined) next.splice(to, 0, item); return next; }
function SetupContext({ step, setup, targetCount, taskCount }: { step: string; setup: ResearchSetup; targetCount: number; taskCount: number }) { return <><div className="context-heading"><b>Research setup</b><span>{step === "setup" ? "Step 1 of 2" : "Step 2 of 2"}</span></div><div className="context-summary"><small>MODE</small><b>{setup.scope === "deep" ? "Deep Research" : "Quick Research"}</b><small>HORIZON</small><b>{setup.timeRange === "3-years" ? "3 years" : setup.timeRange === "12-months" ? "12 months" : setup.customTimeRange || "Custom"}</b><small>TARGETS</small><b>{targetCount} selected</b><small>SOURCE TYPES</small><b>{setup.sourceTypes.length} enabled</b>{step === "plan" && <><small>PLAN TASKS</small><b>{taskCount} questions</b></>}</div><p className="context-note">Evidence and counter-evidence remain separate throughout the research case.</p></>; }
