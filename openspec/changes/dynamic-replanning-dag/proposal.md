## Why

Durable replanning currently only refreshes task definitions that already
exist in a run. A real deep-research runtime must be able to turn newly
identified gaps into additional typed tasks while preserving completed,
independent work.

## What Changes

- Allow a valid replanned plan to add new task contracts.
- Merge new tasks with the existing run instead of dropping them.
- Revalidate the complete merged DAG before persisting it.
- Execute and checkpoint newly added tasks through the existing runtime loop.
- Preserve the run ID, prior evidence, events, and completed independent tasks.

## Capabilities

### New Capabilities

- dynamic-replanning-dag: Extend durable replanning with safe task insertion.

### Modified Capabilities

## Impact

The ResearchEngine replanning merge and its tests; no API shape, dependency, or
FinEvidence change.
