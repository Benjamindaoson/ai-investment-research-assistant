## Context

The backend `ResearchRun` includes `tool_executions`. Each `ToolExecution`
contains an ID, task ID, tool name, `SUCCEEDED`/`FAILED` status, result hash, and
start/completion timestamps. The frontend currently ignores this field.

## Goals / Non-Goals

**Goals:**

- Make execution receipts visible without changing their write authority.
- Keep result hashes and timestamps verbatim from the backend.
- Preserve compatibility with older responses that omit the field.

**Non-Goals:**

- No tool replay, retry, or client-side status changes.
- No fabricated tool output or inference from task state.

## Decisions

- Add a typed `runtimeToolExecutionSchema` with optional run-level array
  defaulting to empty for historical responses.
- Render a compact read-only record per execution.
- Display unavailable states explicitly instead of inferring success.

## Risks / Trade-offs

- Older runs may not carry execution receipts → show an explicit empty state.
- A result hash proves a recorded result identity, not semantic correctness →
  label the section as execution trace only.

## Migration Plan

No migration. This is a frontend read-path enhancement.
