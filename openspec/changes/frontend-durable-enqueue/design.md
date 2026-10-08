## Context

The backend exposes `POST /api/v1/research-runs/{run_id}/enqueue`, which records
a durable queue event for CREATED/PARTIAL runs and leaves terminal runs
idempotent. The frontend service already owns all runtime HTTP parsing, while
the repository and query hooks own the UI dependency direction.

## Goals / Non-Goals

**Goals:**

- Preserve the typed service → repository → query hook → component boundary.
- Expose enqueue as a distinct action with the backend returned run state.
- Make queue submission observable through pending, success, and error states.

**Non-Goals:**

- Do not remove synchronous execute.
- Do not implement a browser worker, polling loop, or client-side queue.
- Do not change the backend queue contract or FinEvidence.

## Decisions

Add `enqueueRun` to `ResearchRuntimeService` and `ResearchRuntimeRepository`.
The HTTP implementation posts an empty JSON body to the existing backend route
and validates the returned `RuntimeRunControl` shape. The unconfigured service
keeps the existing explicit unavailable error.

Add `useEnqueueRuntimeRunMutation` with the same cache invalidation behavior as
execution. The run workspace presents a queue button for CREATED/PARTIAL states
and retains the existing synchronous Start research action for CREATED. After a
successful enqueue, the run query is invalidated so the UI reflects the
persisted control state.

## Risks / Trade-offs

- [Risk] A local worker is not running, so a queued run may remain CREATED or
  RUNNING. → Mitigation: show the returned state and keep the existing refresh
  and synchronous execution controls.
- [Risk] The endpoint may be unavailable. → Mitigation: use the existing typed
  request error path and render the mutation error.

## Migration Plan

No data migration. Deploy frontend and backend independently because the
backend endpoint already exists; older backends simply surface the normal HTTP
error until upgraded.

## Open Questions

None for this bounded integration.
