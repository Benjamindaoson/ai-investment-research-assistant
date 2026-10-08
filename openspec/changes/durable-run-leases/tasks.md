## 1. Persistent lease store

- [x] 1.1 Add the SQLite `run_leases` table and atomic acquire/release operations with expiry takeover.
- [x] 1.2 Add store tests for contention, matching-token release, stale-token protection, and expiry reclamation.

## 2. Runtime and API integration

- [x] 2.1 Wrap non-terminal execution in a per-call lease token and release it in every exit path.
- [x] 2.2 Append lease lifecycle events without changing checkpoint/resume semantics.
- [x] 2.3 Map lease contention to HTTP 409 and preserve explicit failure behavior.

## 3. Verification

- [x] 3.1 Add engine tests for success, provider failure, stop-after-tasks, terminal no-op, and stale lease recovery.
- [x] 3.2 Run backend tests, lint, typecheck, compileall, OpenSpec, CodeGraph, Git checks, and confirm FinEvidence remains untouched.
