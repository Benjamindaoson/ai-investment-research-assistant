## Why

Financial analysis and valuation are reviewable runtime artifacts, but a memo
currently cannot identify which calculation snapshot or scenario artifact it
uses. That breaks the audit chain from investment conclusion to explicit
financial inputs.

## What Changes

- Add optional stable financial-analysis and valuation references to
  InvestmentMemo.
- Update those references when the validated run-scoped artifacts are recorded.
- Expose the references in the typed workspace and Markdown export.
- Keep historical memos readable with null defaults.

## Capabilities

### New Capabilities

- `memo-financial-links`: Stable memo references to run-scoped financial
  artifacts.

### Modified Capabilities

## Impact

- Backend memo contract and financial artifact write projections.
- Frontend memo schema, workspace summary, and export.
- Tests and documentation.
- No calculation, API route, persistence table, or FinEvidence changes.
