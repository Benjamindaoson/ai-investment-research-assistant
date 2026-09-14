## Context

The planner is a safe local fallback and must remain bounded. The existing DAG
already separates market structure, fundamentals, and downside. The missing
piece is semantic intent on each requirement, not more agents or tasks.

## Decision

Keep the existing task IDs and dependency edges. Enrich each requirement with
the minimum slots needed by the external evidence boundary:

- market: explanatory/context support scoped to the target case;
- fundamentals: critical retrieved value support scoped to the target case;
- risk: critical counter evidence scoped to the target case.

The planner does not fill entity, metric, or period because the free-form case
target is not guaranteed to be the exact alias used by the evidence catalog and
the other slots are question-specific. A future mandate-aware planner or
explicit user input may provide exact external slots. The runtime still uses
the case target as the contextual fallback for coverage payloads.

## Non-goals

- No natural-language number extraction.
- No extra planner tasks or agent roles.
- No changes to FinEvidence.
