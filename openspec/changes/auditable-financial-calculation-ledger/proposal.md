## Why

The current financial analysis returns derived metrics and one input hash, but an analyst cannot inspect the exact formula, inputs, unit, or unavailable reason for each metric. That weakens the product's evidence-first promise: a memo can link to evidence while the calculation between evidence and conclusion remains opaque. A calculation ledger is the smallest next step that makes financial outputs reproducible and reviewable without expanding FinEvidence or introducing a new modeling system.

## What Changes

- Add a typed calculation ledger entry for every financial metric produced by the runtime.
- Record the metric name, expression, normalized input values, output value, unit, and availability status.
- Preserve explicit `UNAVAILABLE` entries with a reason instead of silently omitting metrics.
- Include the ledger in the persisted and API-visible `FinancialAnalysisResult`.
- Validate that calculation entries are deterministic and that their input hash remains tied to the analyzed snapshot.
- Expose the ledger in the runtime frontend as a read-only audit surface.
- Add backend, frontend, and contract tests for available, unavailable, zero-denominator, negative, and missing-input calculations.

## Capabilities

### New Capabilities

- `auditable-financial-calculation-ledger`: Evidence-linked financial calculations with per-metric formulas, inputs, outputs, units, and explicit availability states.

### Modified Capabilities

- None.

## Impact

- `backend/research-runtime/src/deepresearch/domain/models.py`
- `backend/research-runtime/src/deepresearch/runtime/financial.py`
- Runtime API and persistence serialization of financial analysis results.
- `apps/web/src/services/research-runtime-service.ts`
- Runtime financial analysis UI and its tests.
- No changes to the frozen FinEvidence repository or its HTTP contract.
