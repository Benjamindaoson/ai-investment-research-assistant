## Why

The research-case read route currently returns a run payload under a case URL.
That violates the domain contract and makes the case endpoint unsafe for clients
that need the original question, target, and creation timestamp.

## What Changes

- Return the persisted `ResearchCase` from `GET /api/v1/research-cases/{case_id}`.
- Add a regression test for the response shape and missing-case 404.

## Capabilities

### New Capabilities

- `research-case-read`: Correct case read semantics at the HTTP boundary.

### Modified Capabilities

None.

## Impact

- One API handler and backend test; no persistence or frontend dependency change.
