## Why

The runtime already persists human decisions in the backend, but the canonical
runtime workspace stops at a memo and red-team review. Analysts therefore cannot
approve, reject, or request further research from the real run surface.

## What Changes

- Expose the existing DecisionRecord contract through the typed runtime service
  and repository.
- Add a query mutation that updates the run and refreshes auditable memory.
- Add an accessible human decision form and decision history to the runtime run
  workspace.
- Keep approval rules in the backend as the source of truth.

## Capabilities

### New Capabilities

- `runtime-human-decision`: Record and display explicit analyst decisions for a
  synthesized runtime thesis.

### Modified Capabilities

## Impact

Frontend runtime service, repository, query hook, run workspace, and tests. No
new backend model, database migration, FinEvidence change, or permission system.
