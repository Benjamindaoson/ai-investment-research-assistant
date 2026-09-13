## Why

Investment research is iterative: an analyst must be able to rerun the same
research case after new evidence or a review request. Unique run identities now
protect history, but the API still lacks a case-scoped rerun entry point.

## What Changes

- Add `POST /api/v1/research-cases/{case_id}/runs` to create a new run from the
  persisted case contract.
- Preserve planner error semantics and return 404 for unknown cases.
- Add regression coverage proving the new run does not overwrite the original.

## Capabilities

### New Capabilities

- `research-case-rerun`: Create independent research runs from an existing case.

### Modified Capabilities

None.

## Impact

- Backend API only; no persistence schema or frontend dependency change.
