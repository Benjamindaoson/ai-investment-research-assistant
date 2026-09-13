import type { RuntimeToolExecution } from "@/services/research-runtime-service";

export function RuntimeToolTrace({ executions }: { executions: RuntimeToolExecution[] }) {
  return <section className="decision-panel runtime-tool-trace">
    <header><div><small>TOOL TRACE · READ-ONLY</small><h2>Execution receipts</h2></div><span>{executions.length} executions</span></header>
    <div className="runtime-tool-list">
      {executions.length === 0 && <p className="form-note">No tool execution receipts returned for this run.</p>}
      {executions.map((execution) => <article className={`runtime-tool-record ${execution.status.toLowerCase()}`} key={execution.id}>
        <header><div><b>{execution.tool_name}</b><small>{execution.task_id} · {execution.id}</small></div><span>{execution.status}</span></header>
        <p>Result hash: {execution.result_hash}</p>
        <footer><span>Started: {execution.started_at}</span><span>Completed: {execution.completed_at}</span></footer>
      </article>)}
    </div>
  </section>;
}
