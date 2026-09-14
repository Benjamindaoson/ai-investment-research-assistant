## Context

The backend exposes `GET /api/v1/research-runs/{run_id}/evaluation` and returns
404 when a run has not been evaluated. Evaluation results contain an evaluator,
pass state, case hash, timestamp, and checks with PASS/FAIL/N/A/BLOCKED states.

## Goals / Non-Goals

**Goals:**

- Validate the full evaluation response at the frontend boundary.
- Show explicit loading, not-evaluated, error, and populated states.
- Keep evaluation state in TanStack Query and avoid coupling it to run control.

**Non-Goals:**

- No frontend authoring of golden cases or evaluation trigger.
- No reimplementation or reinterpretation of the scorer.
- No claim that a missing evaluation is a pass or that a pass is investment
  advice.

## Decisions

1. Model `getEvaluation` as `Promise<EvaluationResult | null>`; only HTTP 404
   from this endpoint becomes `null`, while transport and schema errors remain
   failures.
2. Render the artifact as a read-only checklist. The backend's `passed` value
   is shown as returned, and each check retains its own status and detail.
3. Keep the query independent from `useRuntimeRunQuery` so a missing evaluation
   never replaces or mutates the authoritative run state.

## Risks / Trade-offs

- [Risk] A 404 could represent an invalid run as well as no evaluation →
  Mitigation: the run detail query is authoritative and is loaded first; this
  endpoint's documented 404 semantics are limited to evaluation absence.
- [Risk] The list may become stale after a new evaluation → Mitigation: the
  query refetches on mount/focus under the existing defaults; an explicit
  evaluate action can invalidate it in a later change.

## Migration Plan

No migration. Deploy the frontend against the existing evaluation endpoint.

## Open Questions

None for read-only display.
