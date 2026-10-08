## Context

ResearchPlan is persisted with planner identity, input hash, tasks, and the
normalized mandate. The run page currently parses only execution fields, so the
plan context is not available to an analyst during review.

## Goals / Non-Goals

**Goals:**

- Type and display the plan identity and mandate returned by the runtime.
- Keep the display compatible with historical run responses that omit plan.

**Non-Goals:**

- No plan editing or client-side replanning.
- No change to planner behavior, hash computation, or backend contracts.

## Decisions

- Reuse the existing mandate shape and add a minimal plan schema with optional
  plan on the run response. This prevents a second frontend representation.
- Render the summary as read-only metadata above the task list, with an explicit
  unavailable state for old runs.

## Risks / Trade-offs

- [Historical responses may not include plan] → Use an optional schema field and
  render a clear unavailable message.
- [Required output strings are analyst-entered] → Display them verbatim and do
  not claim that the runtime enforced their financial meaning.

## Migration Plan

No migration. This is a frontend read-path enhancement.
