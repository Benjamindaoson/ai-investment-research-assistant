## Why

The runtime already records thesis-scoped Red-team challenges with
counter-evidence, but the deterministic evaluator does not verify those
artifacts. A corrupted or cross-run challenge could therefore coexist with a
passing golden case and weaken the product's disconfirming-evidence gate.

## What Changes

- Add deterministic Red-team review relation checks to completed and partial
  run evaluation.
- Verify review run/thesis ownership and that every cited evidence record is
  present with COUNTER or CONFLICTING stance.
- Allow golden cases to declare an optional minimum Red-team review count.
- Preserve explicit PASS/FAIL outcomes with sorted IDs and counts.

## Capabilities

### New Capabilities

- `red-team-evaluation`: Deterministic quality gates for Red-team traceability
  and optional review coverage.

### Modified Capabilities

## Impact

- `backend/research-runtime/src/deepresearch/evaluation/scorer.py` and tests.
- Backend evaluation documentation and OpenSpec artifacts.
- No runtime/API schema, persistence, dependency, or FinEvidence changes.
