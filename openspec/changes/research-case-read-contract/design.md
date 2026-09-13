## Context

Cases and runs are separate typed domain objects. The engine already exposes
`get_case`, but the API handler calls `get_run` using the run ID convention.

## Goals / Non-Goals

**Goals:**

- Align URL resource semantics with the domain object returned.
- Preserve 404 behavior without leaking storage details.

**Non-Goals:**

- Adding case listing, editing, or a new frontend route.

## Decisions

Use the existing `engine.get_case(case_id)` directly. This is the smallest
correct fix and avoids duplicating case serialization or deriving a case from a
run.

## Risks / Trade-offs

- [Risk] A client may have depended on the accidental run response → Mitigation:
  the URL and resource name already declare case semantics; clients should use
  the run endpoint for run state.

## Migration Plan

No data migration. Consumers using the route must read case fields; run state is
available at `/api/v1/research-runs/{run_id}`.
