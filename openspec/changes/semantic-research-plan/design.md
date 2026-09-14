## Context

The planner is a safe local fallback and must remain bounded. The existing DAG
already separates market structure, fundamentals, and downside. The missing
piece is semantic intent on each requirement, not more agents or tasks.

## Decision

Keep the existing task IDs and dependency edges. Enrich each requirement with
the minimum slots needed by the external evidence boundary:

- market: explanatory/context support for the target entity;
- fundamentals: critical retrieved value support for the target entity;
- risk: critical counter evidence for the target entity.

The planner does not fill metric or period because those are question-specific
and must be supplied by a future mandate-aware planner or explicit user input.

## Non-goals

- No natural-language number extraction.
- No extra planner tasks or agent roles.
- No changes to FinEvidence.
