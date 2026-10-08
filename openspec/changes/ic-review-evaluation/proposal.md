## Why

The runtime now records role-based IC reviews and links them into memos and
decisions, but the deterministic evaluator does not verify those links. A
review artifact that is present but dangling would therefore pass the product
quality gate, weakening auditability exactly where an investment committee
needs it most.

## What Changes

- Add deterministic IC review link checks to run evaluation.
- Allow golden cases to declare required IC review roles without imposing a
  universal panel-size requirement on lightweight research runs.
- Preserve explicit `PASS`, `FAIL`, and `N/A` outcomes and include missing or
  dangling IDs in bounded check details.
- Add positive and negative tests for memo links, decision links, and required
  role coverage.

## Capabilities

### New Capabilities

- `ic-review-evaluation`: Deterministic quality gates for structured IC review
  traceability and optional role coverage.

### Modified Capabilities

## Impact

- `backend/research-runtime/src/deepresearch/evaluation/scorer.py` and tests.
- No runtime state mutation, new dependency, API change, or FinEvidence change.
