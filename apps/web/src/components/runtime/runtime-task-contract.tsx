import type { RuntimeTask, RuntimeTrace } from "@/services/research-runtime-service";

export function RuntimeTaskContract({ tasks, traceTasks }: { tasks: RuntimeTask[]; traceTasks?: RuntimeTrace["tasks"] }) {
  const traceById = new Map((traceTasks ?? []).map((task) => [task.id, task]));

  return <section className="decision-panel runtime-task-contract">
    <header><div><small>TASK CONTRACT</small><h2>Research tasks</h2></div><span>{tasks.filter((task) => task.state === "COMPLETED").length} / {tasks.length} completed</span></header>
    <div className="runtime-task-list">
      {tasks.length === 0 && <p className="form-note">No research tasks returned for this run.</p>}
      {tasks.map((task) => {
        const traceTask = traceById.get(task.id);
        return <article className="runtime-task" key={task.id}>
          <header><div><b>{task.title}</b><small>{task.id}</small></div><em>{task.state}</em></header>
          <p>{task.purpose ?? "Task purpose unavailable from this response."}</p>
          <footer><span>Tool: {task.tool_name ?? "unavailable"}</span><span>Depends on: {task.depends_on?.length ? task.depends_on.join(", ") : "none or unavailable"}</span>{traceTask ? <span className={traceTask.missing_requirement_ids.length ? "claim-unresolved" : "provenance-complete"}>{traceTask.missing_requirement_ids.length ? `Missing requirements: ${traceTask.missing_requirement_ids.join(", ")}` : "Requirements satisfied"}</span> : <span>Requirement status unavailable from trace.</span>}</footer>
          {task.evidence_requirements ? <div className="runtime-requirement-list">{task.evidence_requirements.map((requirement) => <div key={requirement.id}><b>{requirement.id}</b><span>{requirement.description} · minimum {requirement.minimum_records} · {requirement.required_stances.join(", ")}</span>{requirement.fact_type && <small>{requirement.fact_type} · {requirement.role ?? "role unavailable"} · {requirement.criticality ?? "criticality unavailable"}{requirement.evidence_role ? ` · ${requirement.evidence_role}` : ""}{requirement.entity || requirement.metric || requirement.period ? ` · ${[requirement.entity, requirement.metric, requirement.period].filter(Boolean).join(" / ")}` : ""}</small>}</div>)}</div> : <small className="form-note">Evidence requirements unavailable from this response.</small>}
        </article>;
      })}
    </div>
  </section>;
}
