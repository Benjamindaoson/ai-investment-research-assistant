## Why

The runtime already executes the frozen FinEvidence HTTP path, but its durable
`ToolExecution` receipt only records outcome hashes and failures. An analyst can
therefore see that a task ran without being able to audit which provider and
task contract produced the result or how the evidence response was qualified.

## What Changes

- Extend durable tool receipts with a deterministic task-input hash and the
  selected evidence provider.
- Persist bounded evidence-result counts for total, qualified, review-needed,
  and unqualified records.
- Surface the new receipt fields in the read-only runtime tool trace.
- Preserve backward compatibility for existing SQLite runs and old API
  responses through defaults and optional frontend fields.
- Add backend and frontend contract tests for successful, empty, and failed
  provider executions.

## Capabilities

### New Capabilities

- `finevidence-execution-trace`: durable, bounded audit metadata for each
  evidence-provider execution.

### Modified Capabilities

None. The existing runtime tool-trace behavior is extended through the new
receipt fields; no existing canonical requirement file is available for a
delta spec.

## Impact

- `backend/research-runtime/src/deepresearch/domain/models.py`
- `backend/research-runtime/src/deepresearch/runtime/engine.py`
- `apps/web/src/services/research-runtime-service.ts`
- `apps/web/src/components/runtime/runtime-tool-trace.tsx`
- Related backend and frontend tests.

FinEvidence remains a separate repository and is not modified. No new
dependency, endpoint, retrieval layer, or raw evidence-response storage is
introduced.
