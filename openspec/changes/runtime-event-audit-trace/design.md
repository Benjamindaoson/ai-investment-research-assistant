## Context

`SQLiteStore` already records ordered, run-scoped events and the backend exposes them through a read-only endpoint. The runtime page currently shows derived projections such as task and tool traces, but not the event sequence that explains how those projections were produced. The frontend must preserve the service/repository/query dependency direction and treat event payloads as untrusted transport data.

## Goals / Non-Goals

**Goals:**

- Validate event identity, timestamp, type, and arbitrary JSON payload at the frontend boundary.
- Fetch events independently from the run projection so historical runs remain inspectable.
- Display the newest event first while retaining the event timestamp and full payload for audit inspection.
- Refresh events with the same bounded interval as active run state, then stop polling at terminal states.

**Non-Goals:**

- No event mutation, deletion, replay, or frontend-generated events.
- No new backend event store, websocket, pagination protocol, or event-sourcing rewrite.
- No attempt to turn arbitrary payloads into a second business model in the UI.

## Decisions

1. Use the existing events endpoint and add only the missing typed frontend boundary. This keeps one write authority and avoids duplicating persistence logic.
2. Model `payload` as `Record<string, unknown>` and render stable JSON. Event payload schemas change as runtime capabilities evolve; strict per-event frontend schemas would make historical events brittle.
3. Use a separate TanStack Query keyed by run ID and the run state from its own response to control polling. The event list remains independently readable when the run projection is terminal or stale.
4. Place the trace beside the existing tool/evidence traces and label it read-only. This makes the audit semantics explicit without changing the domain projection.

## Risks / Trade-offs

- [Risk] Payloads may contain large or unexpected nested values → Mitigation: preserve them as JSON and cap only visual formatting, never mutate the stored response.
- [Risk] Event ordering may be ambiguous when timestamps share precision → Mitigation: preserve API array order and display newest-first using a stable reverse traversal.
- [Risk] Historical events may omit fields from newer versions → Mitigation: optional timestamp and payload defaults keep the read surface explicit about unavailable data.

## Migration Plan

No migration. Deploy the frontend against the existing events endpoint. Rollback is removing the event trace component and query without affecting stored runs or event history.

## Open Questions

Pagination and server-side event filtering can be added only when event volume is measured to exceed the current bounded run size.
