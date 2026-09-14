## Context

The runtime already owns `EvidenceRequirement`, while the frozen FinEvidence
coverage API expects typed requirement records. The current HTTP adapter fills
`fact_type`, `role`, `criticality`, and `evidence_role` with constants and
cannot carry metric or period intent from a planner. This makes a research plan
look structured internally while sending a weaker contract across the service
boundary.

## Goals / Non-Goals

**Goals:**

- Preserve the requirement semantics that the planner or explicit caller chose.
- Align the domain fields with the frozen FinEvidence v1 `Requirement` shape.
- Keep existing serialized plans and callers valid through defaults.
- Make the live task-contract UI expose the semantics without replacing the
  existing evidence/review flow.

**Non-Goals:**

- No changes to FinEvidence code or its HTTP endpoints.
- No requirement graph, semantic parser, automatic slot inference, or RAG.
- No new database migration; existing JSON-in-SQLite persistence already
  preserves additive Pydantic fields.

## Decisions

1. Add optional slot fields (`entity`, `metric`, `period`, `segment`, `basis`,
   `geography`, `currency`, `unit`, and `operation`) plus validated
   `fact_type`, `role`, `criticality`, and `evidence_role` to the domain
   requirement. Defaults preserve current plans; fields are serialized as part
   of the existing plan and task contracts.

2. Use the exact finite values defined by the frozen FinEvidence contract for
   `fact_type`, `criticality`, and `evidence_role`. Keep `role` as a bounded
   non-empty string because FinEvidence intentionally leaves domain roles open.
   Reject blank optional slots at the domain boundary rather than silently
   emitting malformed coverage semantics.

3. Build coverage payloads from the requirement object. The target remains the
   fallback entity when a requirement does not provide one; optional fields are
   omitted when absent. Existing provider qualification, citation validation,
   and runtime evidence records are unchanged.

4. Keep frontend fields optional when parsing task responses so old persisted
   runs and older runtime responses remain readable. Render semantic metadata
   separately from the existing description/count/stance line.

## Risks / Trade-offs

- [Older LLM plans omit the new fields] → Defaults retain valid behavior, while
  the planner prompt documents the available structured fields.
- [A caller chooses a role unsupported by its provider deployment] → The
  provider boundary preserves the exact request and surfaces the provider's
  contract/transport error; the runtime does not invent a fallback.
- [Requirements remain manually authored] → This change preserves semantics;
  automatic decomposition is a later planner concern and stays outside this
  boundary.
