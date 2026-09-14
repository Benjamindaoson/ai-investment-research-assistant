## Why

The runtime adapter has a real FinEvidence smoke, but the existing check can
pass when search returns no evidence and does not exercise the HTTP research
run boundary. That leaves the most important integration claim weaker than the
product boundary requires.

## What Changes

- Require the opt-in FinEvidence search smoke to observe at least one real
  evidence object and preserve its identity, citation, and qualification data.
- Add an opt-in API-level smoke covering health, case creation, plan creation,
  run execution, memo retrieval, and event retrieval through the runtime HTTP
  API.
- Keep table lookup as a separately verified empty-result-safe path; a broad
  query is not allowed to assume that a table result exists.
- Keep the default test suite deterministic and do not modify or import
  FinEvidence internals.

## Capabilities

### New Capabilities

- `finevidence-api-runtime-smoke`: Prove the configured runtime can execute a
  research run against the frozen FinEvidence v1 HTTP contract.

### Modified Capabilities

## Impact

- Opt-in backend integration tests and integration documentation.
- No production runtime behavior, persistence schema, frontend, dependency,
  or FinEvidence source changes.
