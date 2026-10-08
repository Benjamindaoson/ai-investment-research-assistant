## Why

The Research Runtime already records deterministic evaluation artifacts, but the
live workspace does not expose them. That makes the product's evaluable claim
invisible to analysts and reviewers, who cannot tell whether a run passed,
failed, or remains not evaluated from the run page.

## What Changes

- Add a typed frontend read for the latest evaluation artifact.
- Treat the runtime's expected evaluation-not-found response as an explicit
  empty state, while preserving other errors.
- Render evaluator metadata and every check status in the live run workspace.

## Capabilities

### New Capabilities

- `runtime-evaluation`: Read and display a durable evaluation artifact without
  conflating absence with success.

### Modified Capabilities

- None.

## Impact

Affected frontend service, repository, query, and runtime presentation only.
No scoring logic, backend API, database, FinEvidence, or new dependency changes.
