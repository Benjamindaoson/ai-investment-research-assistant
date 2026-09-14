import type { RuntimeToolExecution } from "@/services/research-runtime-service";

export function RuntimeToolTrace({ executions }: { executions: RuntimeToolExecution[] }) {
  return <section className="decision-panel runtime-tool-trace">
    <header><div><small>TOOL TRACE · READ-ONLY</small><h2>Execution receipts</h2></div><span>{executions.length} executions</span></header>
    <div className="runtime-tool-list">
      {executions.length === 0 && <p className="form-note">No tool execution receipts returned for this run.</p>}
      {executions.map((execution) => <article className={`runtime-tool-record ${execution.status.toLowerCase()}`} key={execution.id}>
        <header><div><b>{execution.tool_name}</b><small>{execution.task_id} · {execution.id}</small></div><span>{execution.status}</span></header>
        <p>Provider: {execution.provider ?? "unknown"}</p>
        {execution.input_hash && <p>Input hash: {execution.input_hash}</p>}
        {execution.evidence_count !== undefined && <p>Evidence result: {execution.evidence_count} total · {execution.qualified_evidence_count ?? 0} qualified · {execution.review_evidence_count ?? 0} needs review · {execution.unqualified_evidence_count ?? 0} unqualified</p>}
        <p>Attempt: {execution.attempt_key || "historical receipt"}</p>
        <p>Result hash: {execution.result_hash}</p>
        {execution.status === "FAILED" && execution.error_type && <p>Failure: {execution.error_type}: {execution.error_message || "No diagnostic message recorded."}</p>}
        {execution.status === "UNKNOWN_EFFECT" && execution.resolution && <p>Resolution: {execution.resolution}</p>}
        {execution.status === "UNKNOWN_EFFECT" && !execution.resolution && <p>Outcome unknown: explicit operator resolution is required before retry.</p>}
        {execution.status === "FAILED" && execution.error_hash && <p>Diagnostic hash: {execution.error_hash}</p>}
        <footer><span>Started: {execution.started_at}</span><span>Completed: {execution.completed_at || "not recorded"}</span></footer>
      </article>)}
    </div>
  </section>;
}
