## Why

The runtime persists `ToolExecution` records, but the analyst workspace does not
show them. Task completion alone is insufficient for an auditable run: reviewers
need to see which tool executed, whether it succeeded, and which deterministic
result hash was recorded.

## What Changes

- Preserve typed tool-execution records in the runtime run response.
- Add a read-only tool trace with task, status, result hash, and timestamps.
- Keep historical run responses without tool executions compatible.

## Capabilities

### New Capabilities

- `runtime-tool-trace`: Expose durable tool execution records for run review.

### Modified Capabilities

## Impact

Frontend runtime service, run workspace, styles, and tests. No backend,
FinEvidence, planner, persistence, or new dependency changes.
