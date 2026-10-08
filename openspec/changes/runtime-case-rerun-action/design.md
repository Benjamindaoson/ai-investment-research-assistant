## Context

The backend creates a fresh `ResearchRun` from a stored case through
`POST /api/v1/research-cases/{case_id}/runs`. The response contains the new
case and run IDs. Case history is already rendered in the current run page.

## Goals / Non-Goals

**Goals:**

- Keep the rerun action behind the typed service/repository boundary.
- Navigate only after the backend confirms creation.
- Refresh the case-run query after success so the next visit has current
  history.
- Preserve server errors and prevent duplicate clicks while the request is in
  flight.

**Non-Goals:**

- No automatic execution of the new run; creation and execution remain two
  explicit runtime operations.
- No changes to ResearchCase, ResearchRun, memory, planner, or FinEvidence.
- No rerun action for a different case or a synthetic frontend fixture.

## Decisions

1. Use `createCaseRun(caseId)` returning the existing `RuntimeCaseResult`,
   rather than inventing a new response type.
2. Put navigation in the workspace mutation callback, while the history
   component receives a small callback and remains presentational/testable.
3. Invalidate case history after successful creation before navigating. The
   destination run fetch is authoritative; invalidation ensures the source
   history is fresh when revisited.

## Risks / Trade-offs

- [Risk] A user can create multiple runs intentionally or accidentally →
  Mitigation: disable the action during the request and require a second click
  for every new attempt; the backend remains the durable write authority.
- [Risk] Planner configuration can reject creation → Mitigation: show the
  backend error inline and leave the current run untouched.

## Migration Plan

No migration. The existing endpoint is already deployed with the runtime.

## Open Questions

None for the explicit create-only action. Automatic execution remains a later
workflow decision.
