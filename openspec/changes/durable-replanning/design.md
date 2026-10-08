## State transition

Only PARTIAL runs may be replanned:

    PARTIAL
      -> read unresolved requirements
      -> planner replan + DAG validation
      -> reset unresolved tasks and descendants
      -> RUNNING
      -> execute
      -> COMPLETED | PARTIAL | FAILED

COMPLETED, FAILED, and CANCELLED runs remain terminal. The original run ID,
evidence, checkpoints, and append-only events remain durable. Synthesis
artifacts are cleared because they describe the previous incomplete state.

## Plan and task merge

The planner receives the case and unresolved requirement IDs. The returned plan
is validated against the case input hash and task DAG. Existing task IDs are
retained so requirement identity and trace links remain stable; planner output
for new task IDs is ignored in this bounded incremental operation. If the
planner drops every existing task, the replan is rejected. The run resets each
existing task containing an unresolved requirement and every downstream
dependent task. Completed independent tasks are not collected again.

The deterministic planner records the replan context in plan provenance. An
LLM-capable planner may use the same context to produce a revised plan; invalid
or unavailable planner output fails the replan operation without changing the
run.

## Evidence idempotency

Evidence collected during a retry is merged by (record.id, content_hash).
Identical records are ignored, while a changed record remains observable. Trace
coverage counts distinct evidence IDs per task/requirement, preventing retries
from manufacturing coverage through duplicates.
