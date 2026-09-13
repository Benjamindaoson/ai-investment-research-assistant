## Why

Once a case can be rerun, analysts need a stable history read model to compare
and reopen prior execution attempts. Without it, the runtime stores history but
clients must guess or query individual opaque run IDs.

## What Changes

- Add `GET /api/v1/research-cases/{case_id}/runs` returning runs in creation
  order.
- Return 404 for an unknown case and preserve each run's full persisted state.
- Add regression coverage for initial and rerun history.

## Capabilities

### New Capabilities

- `research-case-run-history`: Case-scoped durable run history reads.

### Modified Capabilities

None.

## Impact

- SQLite store, runtime read method, API route, and backend tests only.
