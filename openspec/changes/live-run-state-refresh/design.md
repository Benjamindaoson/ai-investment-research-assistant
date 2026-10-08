## Context

Research execution is durable and lease-based, but the Next.js run page treats
the initial response as a static snapshot. The existing TanStack Query layer is
already the service/repository boundary, so it can observe state without
introducing a second transport or UI-owned timer.

## Goals / Non-Goals

**Goals:**

- Refresh run and trace data only while the run is non-terminal.
- Keep polling policy centralized in the query hooks and testable as a pure
  state-to-interval decision.
- Keep mutation results immediately visible and refresh related cached views.

**Non-Goals:**

- No websocket/SSE transport, background worker, queue, or backend execution
  model change.
- No polling for terminal runs, synthetic workspace data, or unrelated pages.

## Decisions

1. Use TanStack Query's `refetchInterval` with a 2-second interval for
   `CREATED`, `RUNNING`, and `VERIFYING` states; return `false` for undefined or
   terminal state. This reuses the existing server-state owner and avoids a
   custom effect/timer lifecycle.

2. Apply the same policy to the trace query, because task/evidence/tool receipt
   progress is part of the analyst's view of a run. Evaluation and memory keep
   their existing semantics and are invalidated after relevant mutations.

3. Render a concise “live refresh” indicator in the existing run-control panel;
   it communicates observation, not execution completion.

## Risks / Trade-offs

- [Two lightweight GETs every two seconds during an open run] → Scope polling
  to active run pages and stop at terminal states; a future push transport can
  replace the policy if measured load requires it.
- [A failed poll may show stale data] → TanStack Query preserves the last data
  and exposes query errors; the existing manual Refresh/retry control remains.
