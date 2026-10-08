## Why

The runtime already exposes research execution, evidence qualification, financial analysis, valuation, review, decision, and evaluation as separate endpoints. A local user still has to manually discover and sequence those calls, so the product does not yet prove its core value as one runnable investment-research workflow. This change closes that MVP gap without introducing production infrastructure or fabricating analyst judgments.

## What Changes

- Add one single-machine MVP completion workflow that executes a run when needed, then records typed financial facts, evidence-linked financial calculations, three-scenario valuation, red-team review, five-role IC review, human decision, and a deterministic evaluation artifact.
- Require the workflow input to carry explicit typed values, evidence IDs, review rationales, and decision rationale; do not parse arbitrary excerpts or infer investment facts.
- Return a compact workflow receipt containing run state, artifact identifiers, memo state, and evaluation result.
- Make the workflow fail with an actionable validation error when the research run is incomplete, evidence is missing/unqualified, scenario links are invalid, reviews are incomplete, or the decision target is wrong.
- Document one local API/CLI smoke path using the existing SQLite store and deterministic provider; keep FinEvidence available through the existing HTTP boundary.

## Capabilities

### New Capabilities

- `mvp-single-machine-workflow`: A complete, evidence-linked local investment research workflow from research execution through evaluation.

### Modified Capabilities

- None.

## Impact

- Backend runtime API and a small orchestration module.
- Backend API tests, an end-to-end MVP smoke test, and local runtime documentation.
- No changes to FinEvidence, no new external dependencies, and no production deployment infrastructure.
