## Why

The runtime already persists disconfirming reviews, but analysts can only create
them through the API. That leaves the thesis review gate disconnected from the
workstation where evidence, scenarios, and memo readiness are inspected.

## What Changes

- Add a typed HTTP/service/repository path for creating and listing red-team reviews.
- Add a compact runtime form for reviewer, challenge, rationale, outcome, and selected counter-evidence.
- Restrict selectable evidence to the current run's COUNTER or CONFLICTING records.
- Update the cached run projection after a successful review so thesis and memo status changes are visible immediately.
- Surface loading, validation, success, and backend error states without fabricating review results.

## Capabilities

### New Capabilities

- red-team-review-workflow: Create an auditable disconfirming review from the runtime workspace.

### Modified Capabilities

## Impact

Frontend runtime service, repository, query hooks, workspace UI, styles, and tests.
The existing backend contract is reused; FinEvidence remains an external HTTP
evidence qualification boundary and is not modified.
