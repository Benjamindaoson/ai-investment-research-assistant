## Why

`ResearchTask.tool_name` is currently metadata only: the engine sends every
task to one provider regardless of the declared tool. That makes a plan look
typed while allowing an invalid or unintended tool name to execute silently,
which weakens reproducibility and auditability.

## What Changes

- Add a small explicit `ResearchToolRegistry` that resolves task tool names to
  evidence-capable providers.
- Route evidence collection and claim verification through the selected tool
  provider, while preserving the existing single-provider constructor path.
- Fail unknown tool names before provider work and persist the failure through
  the existing ToolExecution receipt semantics.
- Keep compatibility aliases for current deterministic, external, and test
  task names while exposing canonical `evidence.search` registration.
- Add contract tests for registration, selection, unknown-tool failure, and
  provider-specific qualification/verification.

## Capabilities

### New Capabilities

- `research-tool-registry`: explicit task-tool registration and resolution.

### Modified Capabilities

None.

## Impact

- `backend/research-runtime/src/deepresearch/runtime/tools.py`
- `backend/research-runtime/src/deepresearch/runtime/engine.py`
- `backend/research-runtime/src/deepresearch/api.py`
- Backend tests and runtime documentation.

No new dependency, endpoint, queue, agent swarm, or FinEvidence repository
change is introduced.
