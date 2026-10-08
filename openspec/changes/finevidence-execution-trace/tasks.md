## 1. Durable execution contract

- [x] 1.1 Add backward-compatible provider, input-hash, and bounded evidence-count fields to `ToolExecution`.
- [x] 1.2 Populate execution metadata in the leased engine path for success,
  empty results, provider failures, and legacy recovery receipts.

## 2. API and frontend trace

- [x] 2.1 Extend the frontend runtime schema for the additive receipt fields.
- [x] 2.2 Render provider identity, input hash, and qualification counts in the
  existing read-only tool trace.

## 3. Verification and documentation

- [x] 3.1 Add backend tests for deterministic binding, mixed/empty counts,
  failure receipts, and legacy receipt loading.
- [x] 3.2 Add frontend tests for metadata rendering and run the full lint,
  typecheck, test, build, OpenSpec, and CodeGraph checks.
- [x] 3.3 Update runtime documentation to describe the durable execution
  receipt fields and confirm FinEvidence remains an HTTP-only boundary.
