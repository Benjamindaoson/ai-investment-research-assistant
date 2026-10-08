## Why

The runtime response already contains the validated task DAG and evidence
requirements, but the frontend only shows task title, ID, and state. Reviewers
cannot see why a task exists, what it depends on, or which requirements gate its
claim. The execution surface should expose that contract before synthesis is
trusted.

## What Changes

- Preserve detailed task and evidence-requirement fields in the typed run schema.
- Display task purpose, dependencies, and evidence requirements read-only.
- Show missing requirements explicitly and keep historical minimal tasks valid.

## Capabilities

### New Capabilities

- `runtime-task-contract`: Expose the validated task DAG and evidence gates.

### Modified Capabilities

## Impact

Frontend runtime service, task workspace, styles, and tests. No backend,
FinEvidence, planner, persistence, or new dependency changes.
