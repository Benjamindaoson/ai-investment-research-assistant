## Why

Investment Memory is already durable, but a completed live run does not expose
the target-level history that makes the product meaningfully better than a
one-shot research assistant. Analysts need to see whether qualified evidence,
counter-evidence, and unresolved work changed from the prior thesis while
reviewing the current memo.

## What Changes

- Add a read-only run-scoped memory endpoint that resolves the target through
  the persisted case rather than requiring clients to know the target string.
- Add typed frontend transport and a query for run-scoped memory.
- Show prior/current thesis references and observed ThesisDelta in the live run
  workspace, with explicit non-advice wording.

## Capabilities

### New Capabilities

- `runtime-memory-surface`: Read and render target-level memory for a research
  run.

### Modified Capabilities

None.

## Impact

- Backend engine/API read boundary.
- Next.js service, repository, query, and runtime workspace.
- API and frontend transport tests. No persistence schema or dependency change.
