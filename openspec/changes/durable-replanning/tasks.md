## 1. Durable runtime

- [x] 1.1 Add planner replan context and engine state transition.
- [x] 1.2 Merge retry evidence idempotently and preserve task coverage
  semantics.
- [x] 1.3 Expose the replan API with explicit terminal-state errors.
- [x] 1.4 Expose replan through the typed frontend repository, query mutation,
  and partial-run workspace control.

## 2. Verification

- [x] 2.1 Add partial -> replan -> completed tests and duplicate evidence tests.
- [x] 2.2 Update runtime documentation and run backend/static/OpenSpec checks.
