## 1. Specification and audit

- [x] 1.1 Record the master/main/legacy candidate audit and canonical selection.
- [x] 1.2 Create and validate the canonical architecture artifact.

## 2. Runtime contracts and persistence

- [x] 2.1 Add versioned Pydantic domain models for case, run, task DAG, evidence, claim, thesis, decision, execution, checkpoint, and evaluation.
- [x] 2.2 Add a SQLite durable store with transactions, append-only events, checkpoint read-back, and corruption-safe startup.
- [x] 2.3 Add failing contract and store tests, then implement the minimum valid behavior.

## 3. Research execution

- [x] 3.1 Add the FinEvidence provider protocol and deterministic local provider.
- [x] 3.2 Add dependency validation, state transitions, evidence qualification, claim/thesis synthesis, and checkpoint recovery.
- [x] 3.3 Add failing runtime tests and verify resume does not duplicate completed tool executions.

## 4. API and evaluation

- [x] 4.1 Add FastAPI health, case creation, run, read, events, checkpoint, and review endpoints.
- [x] 4.2 Add JSON golden cases and an executable scorer with honest N/A/blocked handling.
- [x] 4.3 Add API and evaluation tests.

## 5. Frontend and cleanup

- [x] 5.1 Retarget the kept frontend fixtures and product specification to financial research semantics.
- [x] 5.2 Update root and backend documentation with run commands and mock/incomplete boundaries.
- [x] 5.3 Delete `legacy_imports` and reject the main-only Iowa/Vite/Figma product from the canonical tree.
- [ ] 5.4 Run lint, typecheck, tests, build, API smoke checks, architecture delivery, and final Git audit.
