## Context

Cases are already stored durably, and runs are stored with a foreign-key-like
`case_id`. The runtime needs a list read that returns case metadata; the
frontend can reuse the existing case-run list to choose the newest run.

## Goals / Non-Goals

**Goals:**

- Make existing cases discoverable from the canonical runtime entry point.
- Keep the list read-only and typed at both backend and frontend boundaries.
- Preserve an explicit empty state and current synthetic mode when no runtime
  URL is configured.

**Non-Goals:**

- No search, pagination, ACL, tenant isolation, deletion, or case editing.
- No new dashboard or duplicate case data in client state.

## Decisions

1. Return stored `ResearchCase` objects directly; their mandate and created time
   are already the canonical case metadata.
2. The frontend loads cases first, then each case's runs only when cases exist;
   it links to the last returned run from the existing ordered history endpoint.
3. If a case has no run (legacy/partial storage), show the case without a
   fabricated link.

## Risks / Trade-offs

- [Risk] Loading runs per case is O(n) requests → Mitigation: keep the first
  inbox bounded by the local runtime's current small scale; add a summary API
  when measured case volume warrants it.
- [Risk] No tenant boundary exists yet → Mitigation: document this as local
  single-user runtime behavior; production ACL remains explicitly incomplete.

## Migration Plan

No migration. Existing rows are read in insertion order.

## Open Questions

Search and pagination require a product/user-volume decision and remain out of
scope.
