## Context

Research execution already persists run state and protects execution with a
durable SQLite lease. A separate process needs a small, explicit way to find
queued or resumable runs while reusing the existing engine rather than
creating a second execution implementation.

## Decision

Add `SQLiteStore.list_runs()` and `ResearchEngine.list_runnable_runs()` as a
bounded local scan of persisted run payloads. The worker considers queued
`CREATED`/`PARTIAL` runs and any `RUNNING` run as the recovery candidate left
by an interrupted executor. A `CREATED` or `PARTIAL` run without a recent
`RUN_ENQUEUED` event is not implicitly executed. Add `POST
/api/v1/research-runs/{run_id}/enqueue`, which appends one `RUN_ENQUEUED`
event for a `CREATED` or `PARTIAL` run and is idempotent for terminal runs.

Add `deepresearch.worker` with:

- `--database` for the SQLite path;
- `--once` to execute each currently runnable run once;
- `--poll-seconds` for a long-lived polling loop.

The worker constructs the normal configured app/runtime, then calls
`ResearchEngine.execute`. Lease conflicts are observed and skipped; provider
failures and blocked states remain in the run projection. The worker does not
mark a run complete itself.

## Non-goals

- No in-process background task pretending to survive process failure.
- No Redis, PostgreSQL, distributed queue, or multi-worker scheduler.
- No change to the existing synchronous execute endpoint.
