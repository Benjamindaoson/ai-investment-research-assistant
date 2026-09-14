## Context

The runtime persists explicit FinancialAnalysis and ValuationScenarios
artifacts. Their write authority rejects unknown and unqualified evidence, but
evaluation must also protect read-back and replay quality gates from malformed
legacy or mutated state.

## Goals / Non-Goals

**Goals:**

- Verify evidence references on present financial artifacts resolve to current
  qualified run evidence.
- Support opt-in artifact-presence requirements in golden cases.
- Keep checks deterministic and free of recalculation.

**Non-Goals:**

- No browser-side arithmetic or formula verification.
- No requirement that every lightweight research run perform a valuation.
- No changes to artifact persistence or FinEvidence.

## Decisions

1. Always emit `financial_artifact_links` and `valuation_artifact_links` for
   terminal runs. An absent artifact passes its link check for compatibility.
2. Add `financial_artifact_presence` and `valuation_artifact_presence` only
   when the case explicitly sets `requires_financial_analysis` or
   `requires_valuation_scenarios` to true.
3. Validate only evidence identity and qualification. The calculation tools
   and domain models remain the authority for formulas and shape.

## Risks / Trade-offs

- [Legacy artifacts may omit optional evidence mappings] → Link checks only
  validate IDs that are present; new artifact writes remain governed by the
  runtime contracts.
- [A case may require an artifact without supplying inputs] → The evaluator
  returns a named FAIL rather than fabricating a result.
