## Why

The deterministic scorer currently prints an `EvaluationResult`, but the result is not attached to a specific `ResearchRun` or stored for later inspection. A research runtime that cannot read back the exact evaluation basis cannot support regression analysis, model promotion, or an auditable quality gate.

## What Changes

- Add run identity, evaluator identity, and golden-case fingerprint to evaluation results.
- Persist evaluation artifacts in the existing SQLite store.
- Add engine and HTTP read/write paths for evaluating a run and retrieving its latest artifact.
- Keep plan and run scoring deterministic and separate; do not manufacture scores for unavailable external capabilities.

## Capabilities

### New Capabilities

- `durable-evaluation`: Persisted, run-bound evaluation artifacts and read-back.

### Modified Capabilities

## Impact

- Evaluation domain model, scorer metadata, SQLite schema, runtime engine, and FastAPI routes.
- Backend tests and API contract tests; no frontend requirement in this slice.
- No new dependency, no change to FinEvidence, and no change to scoring semantics.
