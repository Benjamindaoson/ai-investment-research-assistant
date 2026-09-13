## Context

`ResearchEngine.create_run` already accepts a complete `ResearchCase` and now
creates an opaque unique run. The API can therefore load a persisted case and
reuse the existing planner/validation/persistence path.

## Goals / Non-Goals

**Goals:**

- Make iterative research a first-class API operation.
- Keep case and run contracts separate.
- Preserve no-partial-persistence and planner error behavior.

**Non-Goals:**

- Editing the case question or target.
- Automatic diff planning or monitoring triggers.

## Decisions

Implement a case-scoped POST that calls `engine.get_case` then
`engine.create_run`. The endpoint accepts no client target/question, preventing
the rerun from silently changing the case identity or planner input.

## Risks / Trade-offs

- [Risk] Reruns use the current configured planner and provider → Mitigation:
  each run persists its own plan provenance and evidence, while memory retains
  version references.

## Migration Plan

No migration. The route is additive and old run endpoints remain unchanged.
