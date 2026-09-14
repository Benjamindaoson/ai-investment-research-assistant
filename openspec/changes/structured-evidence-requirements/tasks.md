## 1. Domain contract

- [x] 1.1 Add validated typed semantics and optional slots to
  `EvidenceRequirement` with backward-compatible defaults.
- [x] 1.2 Update planner structured-output guidance and preserve deterministic
  planner compatibility.

## 2. FinEvidence boundary

- [x] 2.1 Serialize requirement-owned fields into the existing coverage
  request, using case target only as the entity fallback.
- [x] 2.2 Add tests for payload propagation, default semantics, invalid input,
  and provider error/provenance behavior remaining unchanged.

## 3. Reviewer surface and verification

- [x] 3.1 Parse and render additive requirement semantics in the live task
  contract with historical-response compatibility.
- [x] 3.2 Run backend/frontend tests, lint, typecheck, build, OpenSpec,
  CodeGraph, HTTP smoke, and Git checks; update docs with the boundary.
