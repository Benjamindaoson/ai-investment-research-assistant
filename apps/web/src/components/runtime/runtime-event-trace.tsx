import type { RuntimeEvent } from "@/services/research-runtime-service";

function formatTimestamp(value: string): string {
  const date = new Date(value);
  return Number.isNaN(date.getTime()) ? "Timestamp unavailable" : date.toLocaleString();
}

export function RuntimeEventTrace({ events, isPending, error }: { events: RuntimeEvent[] | undefined; isPending: boolean; error: Error | null }) {
  return <section className="decision-panel runtime-event-trace" aria-labelledby="runtime-event-trace-heading">
    <header><div><small>AUDIT TRAIL · READ-ONLY</small><h2 id="runtime-event-trace-heading">Run events</h2></div><span>{events?.length ?? 0} events</span></header>
    {isPending && <p className="form-note">Loading durable event history…</p>}
    {error && <p className="form-error" role="alert">Event history unavailable: {error.message}</p>}
    {!isPending && !error && events?.length === 0 && <p className="empty-state">No durable events have been recorded for this run.</p>}
    {!isPending && !error && events && events.length > 0 && <div className="runtime-event-list">
      {events.slice().reverse().map((event) => <details className="runtime-event-record" key={`${event.seq}-${event.event_type}`} open={event === events.at(-1)}>
        <summary><span><b>{event.event_type}</b><small>Sequence {event.seq} · {formatTimestamp(event.occurred_at)}</small></span></summary>
        <pre>{JSON.stringify(event.payload, null, 2)}</pre>
      </details>)}
    </div>}
  </section>;
}
