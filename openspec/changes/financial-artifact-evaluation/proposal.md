## Why

Financial analysis and valuation artifacts already enforce evidence links at
runtime write time, but the deterministic evaluator does not verify them during
replay. A corrupted or incomplete financial artifact could therefore pass a
golden case despite being unsuitable for an auditable investment memo.

## What Changes

- Add deterministic evidence-link checks for financial analysis and valuation
  artifacts when present on completed or partial runs.
- Allow golden cases to explicitly require either financial artifact.
- Report missing and unqualified evidence IDs with stable evaluation details.

## Capabilities

### New Capabilities

- `financial-artifact-evaluation`: Deterministic quality gates for evidence-
  linked financial calculations and valuation scenarios.

### Modified Capabilities

## Impact

- Backend deterministic scorer, tests, documentation, and OpenSpec artifacts.
- No calculation formula, runtime write path, API, dependency, or FinEvidence
  changes.
