## Why

The runtime can stop at a PARTIAL run and can create a separate rerun, but it
cannot use unresolved requirements to continue the same research case. That
breaks the intended loop for evidence-first research: a missing or weak
requirement should produce an explicit, auditable replanning event.

## What Changes

- Add a durable replan operation for partial runs.
- Re-run the planner with the unresolved requirement IDs as context and
  validate the resulting DAG before changing execution state.
- Reset only unresolved tasks and their dependent tasks; retain prior evidence,
  events, and run identity.
- Prevent duplicate evidence from inflating requirement coverage on retry.
- Expose POST /api/v1/research-runs/{run_id}/replan.
- Add tests for partial -> replan -> completed recovery and invalid terminal
  state transitions.

## Non-goals

- No queue, worker, distributed lock, or PostgreSQL migration.
- No automatic model fallback or synthetic evidence after a provider failure.
- No changes to FinEvidence.

## Impact

- Research Runtime engine, planner boundary, API, persistence events, and
  evaluation tests.
- The typed frontend runtime boundary exposes the operation and the live run
  workspace offers a replan control when a run is PARTIAL.
