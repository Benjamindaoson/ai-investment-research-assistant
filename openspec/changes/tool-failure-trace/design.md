## Context

`ResearchRun` already owns a `tool_executions` trace, but the engine only appends a record after a successful provider response. Provider exceptions mark the task and run as failed without recording the invocation that failed. The product requires an evidence-first audit trail, and a failed provider call must never be represented as an empty successful result.

## Goals / Non-Goals

**Goals:**

- Make every completed provider attempt visible in the run trace, including failures.
- Preserve a bounded, safe-to-display error summary and stable hash without storing raw provider responses.
- Keep the existing `ToolExecution` contract backward-compatible for successful records.
- Make failure persistence lease-guarded during execution.

**Non-Goals:**

- No automatic retry policy or `UNKNOWN_EFFECT` classification in this change.
- No provider interface change and no assumption that provider calls are idempotent.
- No change to FinEvidence, evidence qualification, or run terminal-state semantics.

## Decisions

1. Add optional `error_type`, `error_message`, and `error_hash` fields to `ToolExecution`; successful records retain their current shape and failed records carry the bounded diagnostic fields.
2. Create the failure record in the provider exception branch and persist it together with the failed task/run transition. The existing lease-guarded persistence path prevents a stale executor from publishing the trace.
3. Hash the canonical `type:message` diagnostic with SHA-256. Store at most the first 1000 characters of the message to keep trace payloads bounded and avoid persisting full upstream responses.
4. Extend the existing frontend trace schema/component to render the failure diagnostic; no second trace surface is introduced.

## Risks / Trade-offs

- [Risk] An exception message can contain provider-specific details → Mitigation: cap the stored message and store only the exception type plus a diagnostic hash; upstream providers remain responsible for avoiding secrets in exception text.
- [Risk] A process crash before the failure branch still leaves no completed failure record → Mitigation: the existing lease/checkpoint recovery path remains authoritative; an explicit in-flight attempt state is a separate `UNKNOWN_EFFECT` change.
- [Risk] A failure record does not make a retry safe → Mitigation: this change deliberately adds observability only and does not retry provider calls.

## Migration Plan

The new fields are optional, so existing persisted runs validate unchanged. Deploy the backend and frontend together; rollback is safe because old clients ignore the optional fields and old records remain valid.

## Open Questions

The future worker protocol must define how an abandoned in-flight attempt becomes `UNKNOWN_EFFECT` and how an operator resolves or retries it safely.
