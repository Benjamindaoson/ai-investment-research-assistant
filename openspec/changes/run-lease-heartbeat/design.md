## Context

The runtime now has an expiring `run_leases` row, but only acquisition and release are implemented. A provider call can exceed the TTL, allowing a second executor to take over while the first process still has in-memory state. The first process must not overwrite the second process's checkpoint or run payload.

## Goals / Non-Goals

**Goals:**

- Renew active ownership periodically during synchronous execution.
- Make run, checkpoint, and event writes conditional on the current lease token.
- Surface ownership loss as an explicit runtime error.
- Reset abandoned `RUNNING` tasks to `PENDING` when a new lease is acquired.

**Non-Goals:**

- No queue, distributed lock service, or multi-host database migration.
- No attempt to cancel an in-flight provider call from another thread.
- No automatic retry of an evidence provider call whose external effect is unknown.
- No change to FinEvidence or evidence qualification.

## Decisions

1. **Use a standard-library heartbeat thread.**

   A daemon thread renews the lease at one-third of the configured TTL, capped at 30 seconds. The existing synchronous execution remains unchanged; the thread only renews ownership. An event signals renewal failure to the executor.

   Alternative rejected: renewing only between tasks, which still allows a single slow provider call to outlive its lease.

2. **Guard persistence at the SQLite boundary.**

   `save_run_owned`, `save_checkpoint_owned`, and `append_event_owned` verify `(run_id, lease_id, expires_at > now)` in the same transaction as the write. The engine raises `RunLeaseLostError` when any guarded write is rejected. This makes stale in-memory state unable to overwrite a newer owner.

3. **Recover abandoned running tasks on takeover.**

   After successful acquisition, any persisted task in `RUNNING` state is changed to `PENDING` and an explicit `TASK_RECOVERED` event is written. A new executor can then use the existing DAG logic. The provider call itself is not retried automatically before a checkpoint because its external effect is not knowable.

4. **Keep lease lifecycle events ordinary after release.**

   The release event is written after the conditional delete and includes `released` and `heartbeat_lost` flags. This preserves visibility even when the token has become stale.

## Risks / Trade-offs

- [Risk] The heartbeat thread cannot interrupt an in-flight provider call → Mitigation: ownership is checked before all guarded writes; the call's result is discarded if ownership is lost.
- [Risk] A renewal failure can leave a task marked `RUNNING` → Mitigation: the next owner recovers persisted `RUNNING` tasks to `PENDING` before execution.
- [Risk] SQLite remains single-file coordination → Mitigation: scope the guarantee to processes sharing that file; use a database-native worker protocol in the production migration.

## Migration Plan

Additive store methods and a heartbeat wrapper require no data migration. Existing lease rows continue to work. Existing runs with no lease are acquired normally, and old persisted `RUNNING` tasks are recoverable by the new engine.

## Open Questions

The external side-effect/idempotency contract for provider calls remains a separate decision; this change deliberately does not claim exactly-once provider execution.
