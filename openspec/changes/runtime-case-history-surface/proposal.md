## Why

The runtime already persists multiple execution attempts for one ResearchCase,
but the live workspace only exposes the currently opened run. Analysts cannot
inspect how a thesis changed across reruns without leaving the product, which
breaks the audit trail and weakens the Investment Memory workflow.

## What Changes

- Add a typed frontend read for case-scoped runtime run history.
- Add a query hook and a compact history surface to the live run workspace.
- Link each historical run to its durable run page and clearly identify the
  active run and its state.
- Preserve the existing backend API and synthetic frontend boundary.

## Capabilities

### New Capabilities

- `runtime-case-history`: Read and navigate durable runs belonging to one
  ResearchCase.

### Modified Capabilities

- None.

## Impact

Affected frontend service/repository/query contracts and the runtime workspace.
No backend, database, FinEvidence, or new dependency changes are required.
