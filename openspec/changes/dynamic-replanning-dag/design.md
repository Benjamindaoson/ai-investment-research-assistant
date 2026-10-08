## Context

The runtime already records unresolved requirements and resets affected
descendants. The current implementation filters the planner result to the
existing task IDs, which prevents the planner from adding a newly required
research dimension.

## Goals / Non-Goals

**Goals:**

- Accept new tasks returned by a replan.
- Keep old tasks not mentioned by the planner so prior run state is not lost.
- Validate dependencies against the complete merged task set.
- Keep execution, checkpointing, and evidence qualification unchanged.

**Non-Goals:**

- Arbitrary task mutation without planner validation.
- Removing historical tasks or evidence.
- Parallel scheduling changes or a new persistence schema.

## Decisions

Planners declare dynamic task support through the typed planner contract and
may return a full task list. The
runtime merges it with existing tasks by ID and appends planner-only tasks in
PENDING state. Planners without that capability retain the prior behavior:
planner-only tasks are ignored. Existing tasks not returned remain unchanged.
Compute reset descendants from the
unresolved task IDs, then validate the merged plan with the existing case
identity and DAG validators before writing it.

Planner task IDs remain the identity boundary. A duplicate ID is rejected by
the existing DAG validation. A new task may depend only on tasks in the
merged plan; unknown dependencies fail before persistence.

## Risks / Trade-offs

- [Planner adds an overly large plan] → Existing task ceiling is not currently
  enforced by the runtime; add a policy gate when product limits are defined.
- [Planner omits an old task] → Keep omitted tasks in the run, preserving
  audit history and avoiding destructive replans.

## Migration Plan

This is an additive in-place behavior change. Existing replan payloads that
contain only old tasks behave as before. No database migration is required.
