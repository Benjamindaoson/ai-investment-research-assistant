## Why

The Research Runtime currently executes a complete run inside the HTTP request.
That is acceptable for a local demo but prevents long research runs from being
queued, resumed by another process, or operated independently of the API.

## What Changes

- Add an explicit enqueue endpoint that records a durable queue intent without
  pretending the run is already complete.
- Add a worker module that scans persisted runs, acquires the existing durable
  lease, and executes `CREATED` runs or resumes `RUNNING`/`PARTIAL` runs.
- Expose `--once` and polling modes for local operation and restart recovery.
- Keep synchronous execution for compatibility; the worker is an additional
  execution path and uses the same engine, tool registry, checkpoints, and
  failure semantics.

## Capabilities

### New Capabilities

- `durable-research-worker`: Research runs can be explicitly queued and
  executed by a restartable worker process.

### Modified Capabilities

## Impact

- Backend API, SQLite store read path, runtime engine access, worker CLI, and
  tests/documentation.
- No new dependency, no FinEvidence changes, and no frontend change in this
  phase.
