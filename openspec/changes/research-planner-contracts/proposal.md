## Why

The runtime can execute a typed DAG, but callers still need to construct that DAG themselves. That leaves the most important research transition—turning an investment question into bounded, evidence-bearing work—outside the canonical product and makes it impossible to evaluate planning quality independently from execution.

## What Changes

- Add a versioned `ResearchPlan` contract with planner identity, input hash, task DAG, and validation state.
- Add a `ResearchPlanner` boundary and a deterministic planner that produces a minimal financial research DAG without pretending to be an LLM.
- Make `ResearchEngine.create_run` use the planner when tasks are not explicitly supplied, then validate the resulting DAG before persistence.
- Expose the persisted plan through a runtime API endpoint.
- Add planner contract, invalid-plan, persistence, and API tests.
- Document that LLM planning is a future implementation of the planner boundary.

## Capabilities

### New Capabilities

- `research-planning-contract`: Versioned planning output and planner provenance.
- `validated-research-dag`: Validation and persistence of dependency-aware research tasks.

### Modified Capabilities

None.

## Impact

- Backend domain models, runtime engine, API, and tests under `backend/research-runtime`.
- No new dependencies, database migration, external API, or frontend rewrite.
- Existing callers that pass explicit tasks remain compatible; default run creation now records the generated plan.
