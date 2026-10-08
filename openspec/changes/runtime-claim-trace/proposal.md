## Why

The runtime already produces typed claims after evidence qualification, but the
run workspace reduces them to aggregate counts. An analyst cannot inspect the
actual statement, qualification state, confidence signal, or evidence links
without leaving the primary review surface. Claim-level visibility is required
for an auditable evidence-to-thesis chain.

## What Changes

- Preserve the backend claim fields in the typed runtime response.
- Add a read-only claim trace to the runtime run workspace.
- Show claim statement, task, status, confidence, linked evidence, and unresolved
  evidence explicitly when present.
- Keep historical responses with minimal claim objects compatible.

## Capabilities

### New Capabilities

- `runtime-claim-trace`: Expose evidence-linked claims for run review.

### Modified Capabilities

## Impact

Frontend runtime service, run workspace, styles, and tests. No backend,
FinEvidence, planner, persistence, or new dependency changes.
