## Context

The lease heartbeat prevents stale writes but cannot interrupt a provider call. If the process disappears after the provider starts, the next executor can see a persisted `RUNNING` task but cannot know whether the provider completed externally. Treating that task as ordinary `PENDING` silently assumes retry safety.

## Goals / Non-Goals

**Goals:**

- Make the in-flight attempt durable before provider invocation.
- Preserve `UNKNOWN_EFFECT` as a first-class, non-success outcome.
- Prevent automatic retry during takeover.
- Give a human an explicit, auditable choice to authorize retry or mark the attempt failed.

**Non-Goals:**

- No claim of exactly-once execution; the provider interface remains unchanged.
- No automatic timeout cancellation of a synchronous provider call.
- No distributed worker or database migration beyond an additive payload/state contract.

## Decisions

1. Add `attempt_key` to `ToolExecution`, generated as `run_id:task_id:attempt-N`; each retry creates a new record and leaves the prior unknown record intact.
2. Use `UNKNOWN_EFFECT` for both an in-flight persisted attempt and an attempt abandoned during takeover. `completed_at` stays null until the attempt is resolved as failed or succeeds.
3. When takeover finds an unfinished attempt, set the task to `UNKNOWN_EFFECT`, set the run to `BLOCKED`, persist `TOOL_ATTEMPT_UNKNOWN_EFFECT`, and return without provider work. Legacy `RUNNING` tasks without an attempt record receive a synthetic unknown attempt.
4. Add `resolve_tool_attempt(run_id, attempt_id, action)` with `RETRY` or `MARK_FAILED`. `RETRY` resets only the matching task to `PENDING` and the run to `CREATED`; `MARK_FAILED` makes the run terminal `FAILED`. Both actions preserve the unknown attempt and emit an event.
5. Keep the UI read-only in this slice: it must show the blocked state and attempt identity, while the explicit API is the write authority until a dedicated review control is designed.

## Risks / Trade-offs

- [Risk] An operator can authorize a duplicate provider effect → Mitigation: retry is never automatic, attempt history is immutable in the run payload, and the API action is explicit.
- [Risk] A blocked run cannot synthesize a memo → Mitigation: this is intentional; no thesis is produced from unresolved execution state.
- [Risk] Old runs have no attempt record → Mitigation: takeover creates a synthetic attempt with `legacy-recovery` identity and blocks safely.

## Migration Plan

Existing persisted successful/failed tool records remain valid through defaults. Existing runs with `RUNNING` tasks are converted to blocked unknown-effect state only when a new executor takes them over. No schema migration is required for the JSON payload or SQLite tables.

## Open Questions

The production provider contract must expose idempotency keys and receipt reconciliation before retry can be considered safe without human authorization.
