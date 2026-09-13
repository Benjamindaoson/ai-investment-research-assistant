## 1. Structured planner adapter

- [x] 1.1 Add LLM planner configuration, response draft contract, and request/response hashing.
- [x] 1.2 Implement OpenAI-compatible standard-library transport with explicit errors and bounded timeout.
- [x] 1.3 Add mocked transport tests for valid, malformed, HTTP failure, timeout, and secret-free provenance behavior.

## 2. Runtime integration

- [x] 2.1 Add explicit planner selection to API startup configuration with deterministic default.
- [x] 2.2 Add planner selection and failure-path tests proving no silent fallback or partial run persistence.

## 3. Verification and documentation

- [x] 3.1 Document configuration, privacy/cost boundary, and planner evaluation gate.
- [x] 3.2 Run backend lint, typecheck, tests, evaluation, frontend checks, OpenSpec validation, and Git audit.
