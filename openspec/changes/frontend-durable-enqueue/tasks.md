## 1. Typed runtime boundary

- [x] 1.1 Add the enqueue response contract and service method for HTTP and unconfigured implementations.
- [x] 1.2 Expose enqueue through the runtime repository and query mutation with cache invalidation.

## 2. Workspace and verification

- [x] 2.1 Add queue controls and explicit pending/error feedback for CREATED and PARTIAL runs while preserving direct execution.
- [x] 2.2 Add service and hook boundary tests; run frontend lint, typecheck, tests, build, OpenSpec, CodeGraph, and Git checks.
