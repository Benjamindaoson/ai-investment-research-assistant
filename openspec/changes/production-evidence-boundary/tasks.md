## 1. Evidence contract

- [x] 1.1 Extend `EvidenceRecord` with validated source URL, version, locator, content hash, and provenance completeness semantics.
- [x] 1.2 Add versioned provider response models and a standard-library HTTP `EvidenceProvider` adapter with bounded timeout and explicit errors.
- [x] 1.3 Add tests for complete provenance, malformed payloads, unsupported versions, timeouts, and non-2xx responses.

## 2. Runtime trace and failure semantics

- [x] 2.1 Preserve provider failures as task/run events without writing a successful tool execution.
- [x] 2.2 Add a stable run trace summary endpoint with qualification, provenance, missing-requirement, and claim-link data.
- [x] 2.3 Add API tests for completed traces and unknown-run 404 behavior.

## 3. Frontend transport

- [x] 3.1 Implement a typed HTTP ResearchService for the runtime-backed path and validate its responses through existing repository schemas.
- [x] 3.2 Select HTTP transport only from an explicit runtime URL; keep synthetic fixtures as the default local mode.
- [x] 3.3 Add repository/service tests for transport selection and HTTP error propagation.

## 4. End-to-end proof and product boundary

- [x] 4.1 Add an end-to-end contract test proving question → task → evidence → claim → trace and resume semantics.
- [x] 4.2 Update README and product documentation with the enterprise-bank versus individual-investor wedge and FinEvidence ownership boundary.
- [x] 4.3 Run lint, typecheck, frontend tests, backend tests, evaluation, API smoke, and OpenSpec validation; record final Git state.
