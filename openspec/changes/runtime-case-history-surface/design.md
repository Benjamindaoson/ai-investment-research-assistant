## Context

`GET /api/v1/research-cases/{case_id}/runs` already returns durable run
history. The live workspace knows the current run's `case_id`, but the browser
has no typed client or navigation surface for that endpoint.

## Goals / Non-Goals

**Goals:**

- Parse the existing run contract at the frontend HTTP boundary.
- Keep history server state in TanStack Query.
- Show active/current state, run state, and a direct navigation link for each
  run without duplicating run detail data.
- Keep history errors visible but non-blocking to the current run workspace.

**Non-Goals:**

- No new backend endpoint or persistence schema.
- No automatic rerun, deletion, comparison algorithm, or thesis-diff editor.
- No direct mock fixture imports or alternate service path.

## Decisions

1. Reuse `runtimeRunSchema` for each history item so the list cannot silently
   accept a weaker contract than the run detail page.
2. Add `useRuntimeCaseRunsQuery(caseId)` beside the existing run queries. The
   history panel renders loading, error, empty, and populated states locally so
   a history failure does not replace the current run.
3. Use ordinary Next links to `/runtime/{run_id}`. Navigation is reversible,
   shareable, and does not mutate runtime state.

## Risks / Trade-offs

- [Risk] A history list may contain large full run payloads → Mitigation: the
  existing endpoint is the current contract and the UI renders only metadata;
  introduce a summary endpoint only if measured payload size becomes material.
- [Risk] The list can be stale after a rerun → Mitigation: Query refetches on
  mount/focus under the existing TanStack Query defaults; manual workspace
  refresh remains available.

## Migration Plan

No migration. Deploy frontend changes against the existing runtime API. If the
endpoint is unavailable, retain the current run page and show an inline error.

## Open Questions

None for this read-only surface. Thesis comparison belongs in a later,
evidence-aware change.
