## Why

The runtime currently records a run-level failure but omits the failed tool invocation from `ResearchRun.tool_executions`. That breaks the audit chain between a task, its provider call, and the failure observed by the analyst. The failure path needs to be explicit before the runtime is connected to real evidence and data services.

## What Changes

- Record one typed `ToolExecution` with `FAILED` status when a provider call raises.
- Preserve a bounded error type/message and deterministic error hash for the failed invocation.
- Persist the failed tool trace before the terminal `RUN_FAILED` transition.
- Expose failed tool traces through the existing run contract and workspace trace component.
- Keep provider failures distinct from empty evidence and successful execution.

## Capabilities

### New Capabilities

- `tool-failure-trace`: Auditable failure records for provider/tool invocations.

### Modified Capabilities

## Impact

- Backend domain model, synchronous research engine, and runtime tests.
- Existing frontend Zod contract and tool trace presentation.
- No new dependencies, API routes, database migrations, or FinEvidence changes.
