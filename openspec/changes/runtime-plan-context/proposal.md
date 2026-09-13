## Why

The runtime run response contains the validated ResearchPlan, including the
mandate that determined planner identity, but the frontend discards that field.
The execution page therefore cannot prove which decision context the displayed
tasks belong to.

## What Changes

- Preserve the validated plan and mandate in the typed runtime run schema.
- Display the plan mandate and planner identity on the run workspace.
- Keep the summary read-only and sourced only from the backend response.

## Capabilities

### New Capabilities

- `runtime-plan-context`: Make the executed plan's decision context visible.

### Modified Capabilities

## Impact

Frontend runtime service, run workspace, styles, and tests. No backend,
FinEvidence, planner, or persistence changes.
