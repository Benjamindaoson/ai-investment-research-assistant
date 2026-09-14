## Why

The durable worker queue is now a real backend execution path, but the live
workspace only exposes synchronous execution. Analysts need an explicit queue
action so a run can be persisted as work and recovered by the worker after a
browser close or process interruption.

## What Changes

- Add a typed `enqueueRun` method to the frontend runtime service boundary.
- Expose the method through the repository and TanStack Query mutation.
- Add queue controls for CREATED and PARTIAL runs, with explicit queued/error
  feedback and normal polling afterward.
- Keep synchronous execute available for local interactive execution.

## Capabilities

### New Capabilities

- `frontend-durable-enqueue`: The live workspace can submit a run to the
  backend durable worker queue.

### Modified Capabilities

## Impact

- Frontend runtime service, repository, query hook, run workspace, and tests.
- No new dependencies and no backend or FinEvidence changes.
