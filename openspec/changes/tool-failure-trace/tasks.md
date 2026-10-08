## 1. Domain and runtime contract

- [x] 1.1 Extend the backend `ToolExecution` model with optional bounded failure diagnostics.
- [x] 1.2 Record and lease-guard failed provider executions before `RUN_FAILED` persistence.

## 2. Frontend trace surface

- [x] 2.1 Extend the runtime Zod contract for optional failure diagnostics.
- [x] 2.2 Render failure diagnostics in the existing tool trace component without changing successful trace behavior.

## 3. Verification

- [x] 3.1 Add backend tests for failed trace creation, empty-success distinction, bounds, hash, and lease loss.
- [x] 3.2 Add frontend contract/component tests and run backend/frontend checks, OpenSpec, CodeGraph, and Git checks.
