## Why

The runtime persists in-flight research state, but the live workspace only
refreshes on initial load or after a user action. An analyst reopening a run
while another executor is working can therefore see stale task, evidence, and
trace state, weakening the durable/recoverable product promise.

## What Changes

- Poll non-terminal runtime runs at a bounded interval from the existing typed
  service boundary.
- Stop polling once a run reaches a terminal state or the query is disabled.
- Refresh the run trace alongside the run state and invalidate related cached
  views after execution, replanning, or cancellation.
- Expose the live-refresh state in the run-control surface and add hook tests.

## Capabilities

### New Capabilities

- `live-run-state-refresh`: The live workspace observes durable in-flight run
  state and stops refreshing at terminal outcomes.

### Modified Capabilities

## Impact

- `apps/web/src/queries/use-runtime-run.ts` and its tests.
- `apps/web/src/components/runtime/runtime-run-workspace.tsx`.
- No backend API, dependency, websocket, queue, or FinEvidence change.
