## Why

The planner boundary now exists, but there is no independent measurement of whether a plan covers the required financial questions, encodes useful dependencies, requests evidence, and tests disconfirming conditions. Without a planning evaluation baseline, an LLM planner could increase prose quality while reducing research quality.

## What Changes

- Add planner golden cases with expected task coverage, dependency edges, evidence requirements, and counter-evidence requirements.
- Add an executable `score_plan` evaluator with explicit PASS/FAIL/N/A semantics.
- Extend the local evaluation command to score both the plan and the executed run.
- Add tests for a passing deterministic plan and failing plans with missing coverage or invalid structure.
- Document planner quality as a separate evaluation dimension from runtime execution quality.

## Capabilities

### New Capabilities

- `planner-quality-evaluation`: Independent, deterministic evaluation of research plan quality.

### Modified Capabilities

None.

## Impact

- Backend evaluation package and golden cases under `backend/research-runtime`.
- Planner tests and evaluation CLI output.
- No new dependencies, model provider, prompt, RAG system, or production data connector.
