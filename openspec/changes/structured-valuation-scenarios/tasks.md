## 1. Domain and calculation contract

- [x] 1.1 Add typed Bull/Base/Bear input and output models with Decimal bounds and nullable run artifact compatibility.
- [x] 1.2 Implement deterministic scenario calculations, stable input hashing, and validation for evidence-link keys and terminal spread.

## 2. Durable runtime and API

- [x] 2.1 Add run-level evidence qualification validation and durable persistence/event recording for the scenario artifact.
- [x] 2.2 Add POST/GET valuation-scenarios API routes with 404/422 error boundaries.
- [x] 2.3 Extend frontend runtime schemas, repository/service transport, and read-only workspace rendering.

## 3. Verification

- [x] 3.1 Add backend calculation, qualification, persistence, and API read-back tests plus frontend schema/render tests.
- [x] 3.2 Run backend/frontend tests, lint, typecheck, build, compileall, OpenSpec, CodeGraph, and Git checks.
