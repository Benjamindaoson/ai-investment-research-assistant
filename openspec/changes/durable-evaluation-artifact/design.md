## Context

`score_plan` and `score_run` already produce named PASS/FAIL/N/A checks. They currently return transient Pydantic objects from the CLI/tests, so a later analyst or regression job cannot prove which run and golden case produced a result. SQLite is the current durable runtime store and already owns run events.

## Goals / Non-Goals

**Goals:**

- Bind a run evaluation to `run_id`, `case_id`, evaluator name/version, and a stable input hash.
- Persist the complete check list and read it back with strict domain validation.
- Add an explicit evaluate route that accepts a JSON golden-case contract and rejects a case ID that does not match the run.
- Record an `EVALUATION_RECORDED` event after successful persistence.

**Non-Goals:**

- No weighted score, leaderboard, model-promotion policy, or external benchmark runner.
- No persistence of planner evaluation results in this change; plan scoring remains a separate CLI concern.
- No claim that a passing deterministic scorer proves investment correctness.

## Decisions

1. Extend `EvaluationResult` with backward-compatible metadata (`run_id`, `evaluator`, `case_hash`) and compute the case hash from stable sorted JSON.
2. Add one SQLite `evaluations` table keyed by artifact ID, storing the complete JSON payload. A run may have multiple evaluation artifacts; the API returns the latest by insertion order.
3. Put orchestration in `ResearchEngine.evaluate_run`: load the run, enforce `case.case_id == run.case_id`, call the existing `score_run`, attach `run_id`, persist, and append the event. The scorer remains pure.
4. Use a small request body containing `case: dict[str, Any]`; the caller supplies the independently authored golden contract, while the stored hash makes later read-back explicit.

## Risks / Trade-offs

- [Risk] An API caller can submit a weak golden case → Mitigation: persist the exact case hash and keep authored golden files/CI as the evaluation authority; this route is an artifact writer, not a trust oracle.
- [Risk] Re-evaluating a run creates multiple artifacts → Mitigation: preserve all artifacts and return latest, enabling comparison rather than overwriting history.
- [Risk] SQLite is local-file durability only → Mitigation: retain a replaceable store boundary for a future worker/database migration.

## Migration Plan

The table is created additively at store initialization. Existing `EvaluationResult` payloads remain valid because new metadata is optional/defaulted. No data migration is required.

## Open Questions

The production evaluation service needs an immutable case registry and promotion gate before model outputs influence defaults.
