## Context

ResearchCase is the durable root of the runtime, but its current input is
limited to question and target. Planner input hashes and LLM prompts therefore
cannot preserve the decision context that makes a research plan meaningful.
The existing SQLite store persists whole validated JSON payloads, so the
mandate can be added without a database migration.

## Goals / Non-Goals

**Goals:**

- Make decision context explicit before a plan is generated.
- Include that context in the immutable planner input identity.
- Keep old cases readable through validated defaults.
- Keep the frontend input typed and honest.

**Non-Goals:**

- No mandate authorization, ACL, or multi-user ownership model.
- No automatic interpretation of free-form constraints.
- No redesign of the existing task planner or evidence provider.
- No new market-data or RAG integration.

## Decisions

- Model ResearchMandate as a nested Pydantic value object with bounded enums
  and lists. This keeps the case contract explicit and prevents arbitrary
  anonymous metadata from becoming planner state.
- Use stable defaults for omitted mandate fields so older API clients and
  stored cases remain valid. The full normalized mandate is still included in
  the input hash.
- Carry the mandate onto ResearchPlan and validate case/plan equality before
  persistence. A planner that omits or changes the mandate cannot silently
  produce a plan for a different decision context.
- Represent required outputs as an explicit list and constraints as explicit
  strings. The runtime preserves them but does not parse or infer their
  financial meaning.

## Risks / Trade-offs

- [Existing custom planners may not set the new plan field] → Give the plan
  field a default and validate equality; update the canonical planners and
  keep compatibility for old test fixtures.
- [List ordering changes the hash] → Preserve user-provided order because it is
  part of the explicit mandate; callers that need canonical identity must
  submit stable ordering.
- [Free-form constraints can be vague] → Store them verbatim and surface them
  for later planner/evaluation work rather than pretending they are enforced.

## Migration Plan

No database migration. New cases accept the mandate. Existing persisted cases
load with defaults, while newly generated plans record the normalized mandate.
