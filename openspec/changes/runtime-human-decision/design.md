## Context

The backend already owns DecisionRecord validation, state transitions, memory
updates, and the `/api/v1/research-runs/{run_id}/decisions` endpoint. The
frontend runtime workspace currently has no typed path to that endpoint, so
human review is incomplete at the product boundary.

## Goals / Non-Goals

**Goals:**

- Keep decision validation and approval eligibility in the backend.
- Add a replaceable typed service/repository boundary and a cache-aware query
  mutation.
- Make analyst identity, action, target thesis, and rationale explicit.
- Show immutable decision history from the run response.

**Non-Goals:**

- No new decision model or database migration.
- No authentication or authorization; the current local runtime has no identity
  provider.
- No automatic approval, model-generated decision, or portfolio order routing.

## Decisions

- Use the existing `DecisionRecord` API rather than adding a second review
  endpoint. This preserves one backend write authority and avoids duplicate
  semantics.
- Add a small dedicated form component to the runtime page. It receives the
  current run and submits the thesis ID explicitly, so decisions cannot be
  detached from the displayed thesis.
- Update the run cache with the backend response and invalidate memory after a
  decision because the backend appends the decision ID to Investment Memory.
- Render prior decisions as read-only audit history. Editing or deleting a
  decision would violate the append-only event semantics.

## Risks / Trade-offs

- [The local runtime has no authenticated user] → Require an explicit analyst
  name in the form and keep authorization out of this change.
- [Approval can fail for incomplete runs] → Preserve backend rejection and show
  its error; do not weaken the rule in the UI.
- [The run response may come from an older backend without decisions] → Parse
  the field with an empty-list default for backwards-compatible reads.

## Migration Plan

No migration. Deploy the frontend against the existing endpoint. If the endpoint
is unavailable, the typed service exposes the HTTP error and leaves the cached
run unchanged.

## Open Questions

Authentication and role-based approval authority remain deployment concerns for
the future production runtime.
