## 1. Domain and scorer metadata

- [x] 1.1 Add backward-compatible run/evaluator/case-hash metadata to `EvaluationResult` and stable case hashing.

## 2. Durable runtime and API

- [x] 2.1 Add SQLite evaluation persistence and latest-artifact read-back.
- [x] 2.2 Add engine evaluate/read methods with case identity validation and event trace.
- [x] 2.3 Add FastAPI evaluate and latest-evaluation routes with explicit error boundaries.

## 3. Verification

- [x] 3.1 Add scorer, store, engine, and API tests for persistence, reconstruction, history, mismatch, and N/A semantics.
- [x] 3.2 Run backend tests, lint, typecheck, compileall, frontend checks, OpenSpec, CodeGraph, and Git checks.
