## Context

`InvestmentMemory` is written during memo synthesis and currently requires a
target path parameter. The live run route only has a run ID, and the frontend
does not have a safe way to discover the target without duplicating case state.

## Goals / Non-Goals

**Goals:**

- Resolve memory from a run through the canonical backend state.
- Preserve the existing typed service/repository dependency direction.
- Surface only observed history and explicit thesis IDs; never present a delta as
  model confidence or investment advice.

**Non-Goals:**

- Editing memory from the UI.
- Automatic monitoring, alerts, or new data retrieval.
- A separate history database or client-side memory cache.

## Decisions

1. Add `ResearchEngine.get_memory_for_run(run_id)` so target resolution stays
   in the runtime domain boundary and is reusable by HTTP adapters.
2. Return the existing `InvestmentMemory` contract unchanged. The new endpoint
   is only a lookup convenience and does not create another representation.
3. Enable the frontend query only after the run has a memo, because memory is
   created during synthesis; a missing memory remains a visible query error
   rather than fabricated empty history.

## Risks / Trade-offs

- [Risk] A historical run may reference a target with no memory because it was
  created before synthesis → Mitigation: return 404 and keep the UI silent for
  that expected pre-synthesis state.
- [Risk] The live page can show stale memory after a new execution → Mitigation:
  invalidate the memory query when execution succeeds.

## Migration Plan

No migration is required. Existing memory payloads are returned as-is, and the
new route is additive.

## Open Questions

Monitoring triggers and analyst-authored memory annotations require a separate
write contract after the evidence provider boundary is production-ready.
