## 1. Workflow implementation

- [x] 1.1 Add the typed MVP request and receipt models without duplicating domain validation.
- [x] 1.2 Implement the ordered single-machine orchestration using the existing engine, financial, valuation, review, decision, and evaluation paths.
- [x] 1.3 Expose `POST /api/v1/research-runs/{run_id}/mvp-complete` with actionable 404/409/422 errors.

## 2. Verification and documentation

- [x] 2.1 Add API tests for successful completion, evidence rejection, incomplete IC coverage, and persisted artifact retrieval.
- [x] 2.2 Add a local MVP smoke command or fixture that runs against SQLite and the deterministic provider.
- [x] 2.3 Document the canonical single-machine flow, its explicit-input boundary, and its deterministic/FinEvidence modes.
- [x] 2.4 Run backend tests, lint, typecheck, compileall, OpenSpec validation, and CodeGraph status; fix failures before delivery.
