## Context

The runtime API already accepts a reviewer, challenge, rationale, outcome, and
counter-evidence IDs and returns the updated durable ResearchRun. The frontend
currently renders existing reviews but has no creation path. This change spans
the typed service boundary, repository, query cache, and runtime workspace.

## Goals / Non-Goals

**Goals:**

- Make disconfirming review a first-class action in the runtime workspace.
- Keep review evidence selection constrained to counter or conflicting evidence
  already observed in the current run.
- Preserve the backend response as the source of truth for thesis and memo
  status changes.
- Make rejected requests visible without creating a local fake review.

**Non-Goals:**

- No new backend endpoint or schema migration.
- No automatic challenge generation or LLM call.
- No approval workflow beyond recording the selected review outcome.

## Decisions

- Extend the existing runtime service and repository with create/list methods,
  rather than calling fetch from the component. This preserves the existing
  Page → Query → Repository → Service boundary and keeps HTTP validation in one
  place.
- Add one mutation hook that writes the returned ResearchRun to the existing
  run query key. A local review store or optimistic append would risk showing a
  review the backend rejected.
- Use a native form with reviewer, challenge, rationale, outcome, and a
  multi-select evidence control. The evidence options are derived from the
  current run and filtered by COUNTER/CONFLICTING stance; backend validation
  remains authoritative.
- Keep the form available only when a synthesized thesis and disconfirming
  evidence exist. This avoids a review action that cannot satisfy the runtime
  contract.

## Risks / Trade-offs

- [Evidence labels may be opaque] → Show source title when available and always
  show the evidence ID.
- [Multiple evidence selection is less discoverable than a custom picker] →
  Use a native multiple select with explicit helper text and preserve keyboard
  accessibility.
- [The outcome is analyst-entered] → Keep it explicit and persist the exact
  submitted rationale; do not infer an outcome from the challenge text.

## Migration Plan

No migration. Existing runs and review projections remain readable. The form is
additive and only appears when the run has a thesis plus counter/conflicting
evidence.
