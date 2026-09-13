import type { RuntimePlan } from "@/services/research-runtime-service";

export function RuntimePlanContext({ plan }: { plan?: RuntimePlan }) {
  return <section className="decision-panel runtime-plan-context">
    <header><div><small>VALIDATED PLAN · READ-ONLY</small><h2>Decision context</h2></div><span>{plan?.status ?? "unavailable"}</span></header>
    {!plan && <p className="form-note">Plan context is unavailable in this historical run response.</p>}
    {plan && <div className="runtime-plan-grid"><span><b>Planner</b>{plan.planner_name} · {plan.planner_version}</span><span><b>Decision</b>{plan.mandate.decision_type}</span><span><b>Horizon</b>{plan.mandate.time_horizon}</span><span><b>Materiality</b>{plan.mandate.materiality}</span><span><b>Required outputs</b>{plan.mandate.required_outputs.join(" · ")}</span><span><b>Input hash</b>{plan.input_hash}</span>{plan.mandate.constraints.length > 0 && <span><b>Constraints</b>{plan.mandate.constraints.join(" · ")}</span>}</div>}
  </section>;
}
