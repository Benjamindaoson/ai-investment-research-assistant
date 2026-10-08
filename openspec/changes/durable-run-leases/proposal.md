## Why

The runtime checkpoints state between tasks, but concurrent execute requests can still observe the same run and invoke an evidence provider twice. That creates duplicate tool work and ambiguous audit history. A short-lived persistent lease closes this correctness gap while preserving crash recovery: an expired lease can be reclaimed by a later execution attempt.

## What Changes

- Add a SQLite-backed lease for each active research run with a unique lease token and expiry.
- Make execute acquire the lease atomically before doing work and release it in all exit paths.
- Reject concurrent execution with an explicit HTTP 409 instead of running duplicate provider work.
- Record lease acquisition and release as append-only run events.
- Allow a later worker to reclaim an expired lease and resume from the persisted checkpoint.
- Add tests for contention, expiry takeover, release on provider failure, and API error mapping.

## Capabilities

### New Capabilities

- `durable-run-leases`: Persistent, expiring execution ownership for research runs.

### Modified Capabilities

- None.

## Impact

- SQLite persistence schema and store API.
- Research engine execution boundary and runtime API error handling.
- Backend tests and local run documentation.
- No new dependency, worker framework, or FinEvidence change.
