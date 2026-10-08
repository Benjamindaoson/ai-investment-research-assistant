## Why

Red-team reviews are durable run artifacts, but the investment memo currently
records only their counter-evidence IDs. Without the review IDs, a reviewer
cannot trace the memo's disconfirming analysis back to the challenge, outcome,
and rationale that produced it.

## What Changes

- Add `red_team_review_ids` to the durable InvestmentMemo contract.
- Automatically append each accepted Red-team review ID to the current memo.
- Expose the relationship through the typed frontend and Markdown export.
- Preserve backward compatibility for historical memos with no field.

## Capabilities

### New Capabilities

- `red-team-memo-links`: Evidence-linked Red-team review references in memo
  projections and exports.

### Modified Capabilities

## Impact

- Backend domain model and runtime write projection.
- Frontend service contract, workspace memo summary, and memo export.
- Backend/frontend tests and documentation.
- No FinEvidence or review decision semantics change.
