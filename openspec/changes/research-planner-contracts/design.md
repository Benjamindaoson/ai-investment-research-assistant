## Context

Research execution is only as reliable as the task contract that precedes it. The current engine has a useful default task list hidden inside the engine, but it has no first-class plan object or planner provenance. A future LLM planner must be able to replace the deterministic implementation without changing persistence, validation, execution, or API consumers.

## Goals / Non-Goals

**Goals:**

- Make a research plan a persisted, versioned domain object.
- Keep planning separate from execution and enforce validation before persistence.
- Record planner name, planner version, and deterministic input hash.
- Provide a stable plan API and tests for invalid planner output.

**Non-Goals:**

- Calling an LLM, adding prompt templates, or adding provider credentials.
- Solving arbitrary natural-language planning or optimizing task parallelism.
- Adding a second runtime, queue, workflow framework, or graph database.

## Decisions

1. **Use a `ResearchPlanner` protocol.** The runtime depends on a small `plan(case)` method. `DeterministicResearchPlanner` is the local implementation; an LLM planner can later implement the same boundary.

2. **Persist plan metadata alongside the run.** A `ResearchPlan` stores the planned tasks, planner identity/version, input hash, and validation status. The run keeps its execution task state separately so execution mutation does not rewrite planning provenance.

3. **Validate before persistence.** The engine validates unique IDs, dependency references, cycles, and non-empty evidence requirements before saving either case or run. Invalid planner output is a failed request, not a persisted partial run.

4. **Keep the deterministic plan intentionally small.** It covers market structure, financial fundamentals, and downside/disconfirming evidence. This is enough to prove the contract and leaves domain expansion to evidence/tool capabilities rather than speculative planner complexity.

## Risks / Trade-offs

- [A deterministic planner is not intelligent] → Label it explicitly and keep the planner boundary replaceable.
- [Plan and run contain related task data] → Keep plan tasks immutable in intent and run tasks mutable in execution state; expose both clearly.
- [Future planner output may be unsafe] → Preserve pre-persistence DAG and evidence-requirement validation as a mandatory boundary.

## Migration Plan

1. Add the plan model and planner protocol.
2. Move the existing default task definition into the deterministic planner.
3. Persist the plan during run creation and add the plan endpoint.
4. Run existing tests and new planner/API tests.
5. Roll back by supplying explicit tasks to `create_run`; no schema migration is required because run payloads are JSON.

## Open Questions

- The eventual LLM planner's model, prompt, and provider remain deliberately undecided until real planning evaluation cases exist.
