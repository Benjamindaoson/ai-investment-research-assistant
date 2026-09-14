## 1. Durable queue boundary

- [x] 1.1 Add persisted run listing and `ResearchEngine` runnable-run access.
- [x] 1.2 Add idempotent enqueue API and `RUN_ENQUEUED` event behavior.

## 2. Worker

- [x] 2.1 Add one-shot and polling worker CLI using the existing engine and
  lease.
- [x] 2.2 Add tests for enqueue, worker completion, interrupted-run resumption, and
  lease conflict behavior.

## 3. Verification

- [x] 3.1 Run backend tests, Ruff, mypy, and compileall.
- [x] 3.2 Run OpenSpec, CodeGraph, and Git checks.
