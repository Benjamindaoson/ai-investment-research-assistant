import type { EvaluationResult } from "@/services/research-runtime-service";

function resultLabel(passed: boolean | null): string {
  return passed === true ? "PASS" : passed === false ? "FAIL" : "NOT DETERMINED";
}

export function RuntimeEvaluation({ evaluation, isPending, error }: { evaluation: EvaluationResult | null | undefined; isPending: boolean; error: Error | null }) {
  return <section className="decision-panel runtime-evaluation" aria-labelledby="runtime-evaluation-heading">
    <header><div><small>EVALUATION · READ-ONLY ARTIFACT</small><h2 id="runtime-evaluation-heading">Run quality checks</h2></div><span>{evaluation ? resultLabel(evaluation.passed) : "Not evaluated"}</span></header>
    {isPending && <p className="form-note">Loading evaluation…</p>}
    {error && <p className="form-error" role="alert">Evaluation unavailable: {error.message}</p>}
    {!isPending && !error && !evaluation && <p className="empty-state">No evaluation artifact has been recorded for this run.</p>}
    {!isPending && !error && evaluation && <><p className="form-note">{evaluation.evaluator} · evaluated {new Date(evaluation.evaluated_at).toLocaleString()}</p><div className="runtime-evaluation-checks">{evaluation.checks.map((check) => <article key={check.name}><header><strong>{check.name}</strong><span className={`evaluation-status ${check.status.toLowerCase().replace("/", "-")}`}>{check.status}</span></header><p>{check.detail}</p></article>)}</div></>}
  </section>;
}
