## Why

Persistent run leases prevent concurrent execution, but a fixed TTL is unsafe for a slow evidence provider: a healthy executor can outlive its lease and become a stale writer. Heartbeat renewal and ownership-checked persistence are required before the runtime can safely handle long-running research tasks.

## What Changes

- Add lease renewal and ownership-check operations to the SQLite store.
- Run a bounded standard-library heartbeat while a research run executes.
- Stop stale executors from persisting run state, checkpoints, or events after ownership is lost.
- Recover tasks left in `RUNNING` state when a new executor legitimately takes over.
- Preserve explicit lease-loss errors and audit the outcome.
- Add slow-provider, renewal-loss, and recovery tests.

## Capabilities

### New Capabilities

- `run-lease-heartbeat`: Renewable execution ownership and stale-writer protection for long-running research runs.

### Modified Capabilities

- None.

## Impact

- SQLite lease and ownership-checked persistence methods.
- Research engine execution and recovery behavior.
- Backend API conflict/error mapping, tests, and runtime documentation.
- No new dependency and no changes to FinEvidence.
