## Context

The backend serializes each `Claim` with `id`, `task_id`, `statement`,
`evidence_ids`, `status`, and `confidence`. It may also expose
`unresolved_evidence_ids` through the trace projection. The frontend currently
parses only a reduced claim shape and renders no claim-level review component.

## Goals / Non-Goals

**Goals:**

- Keep claim data typed at the service boundary.
- Make each claim's evidence relationship inspectable without implying that
  model confidence is investment certainty.
- Preserve compatibility with historical responses that lack detailed fields.

**Non-Goals:**

- No claim editing, approval, or client-side verification.
- No new backend endpoint or FinEvidence call.
- No inferred claim text, evidence, or qualification state.

## Decisions

- Extend the existing runtime claim schema with optional detailed fields and an
  exported `RuntimeClaim` type.
- Render one compact read-only record per claim, using explicit unavailable
  labels for omitted historical fields.
- Link evidence IDs to the existing evidence trace by displaying the IDs and
  qualification context already returned by the run response.

## Risks / Trade-offs

- Historical claims may contain only IDs and status → retain optional fields and
  show a compatibility message instead of rejecting the whole run.
- Confidence is a model/runtime signal, not a probability of investment success
  → label it as claim confidence and show the bounded percentage only.

## Migration Plan

No migration. This is a frontend read-path enhancement.
