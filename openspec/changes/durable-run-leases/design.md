## Context

`ResearchEngine.execute` persists checkpoints, but ownership is not persisted. Two HTTP requests can therefore enter the same run concurrently, and a process crash leaves no explicit distinction between active ownership and abandoned work. The runtime needs a small coordination primitive before it can be safely moved behind a worker or retried by an operator.

## Goals / Non-Goals

**Goals:**

- Enforce one active executor per run across runtime processes sharing SQLite.
- Make ownership recoverable after expiry without manual database repair.
- Keep lease acquisition and release observable in the existing append-only event stream.
- Return a stable conflict response to callers instead of duplicating provider work.
- Preserve current checkpoint-based resume behavior.

**Non-Goals:**

- No distributed consensus or cross-database lock service.
- No background worker or queue in this slice.
- No lease renewal protocol; execution remains bounded by a configured TTL.
- No change to FinEvidence or evidence semantics.

## Decisions

1. **Use a SQLite `run_leases` table with `run_id` as the primary key.**

   Acquisition is an insert inside the store's transaction. A unique constraint makes contention atomic across processes. Expired rows are deleted during acquisition, allowing takeover after a crash.

   Alternative rejected: an in-memory `threading.Lock`, which cannot coordinate multiple Uvicorn workers and disappears on process failure.

2. **Use an opaque per-execution lease token.**

   Release deletes only the matching `(run_id, lease_id)` row. A stale executor cannot release a newer owner's lease after expiry and takeover.

3. **Wrap the existing execute body in a lease boundary.**

   Terminal runs return without acquiring a lease. Non-terminal runs acquire before provider work, append `RUN_LEASE_ACQUIRED`, run the existing checkpointed execution, then release in `finally` and append `RUN_LEASE_RELEASED`. Contention raises a typed error mapped to HTTP 409.

4. **Use a bounded default TTL.**

   The engine defaults to 300 seconds, with an optional runtime environment override. This is intentionally a ceiling for the current synchronous execution path; a future heartbeat protocol must replace it before tasks can exceed the TTL.

## Risks / Trade-offs

- [Risk] A task can legitimately exceed the TTL → Mitigation: choose the timeout above the current provider timeout and document the ceiling; add heartbeat before long-running production workers.
- [Risk] SQLite is not a multi-host coordination backend → Mitigation: scope this guarantee to processes sharing the same SQLite file and make PostgreSQL/worker coordination a later migration.
- [Risk] Release-event persistence can fail after work succeeds → Mitigation: lease deletion is attempted in `finally`; the run result remains persisted by the existing checkpoint/event path and the next acquisition can recover an expired row.

## Migration Plan

The store creates `run_leases` with `CREATE TABLE IF NOT EXISTS`; no destructive migration is required. Existing runs have no lease row and remain executable. Rollback is safe because older code ignores the additional table and events.

## Open Questions

The production heartbeat interval and worker ownership model should be decided when asynchronous execution is introduced.
