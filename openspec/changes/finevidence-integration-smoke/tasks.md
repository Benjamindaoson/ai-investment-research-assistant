## 1. Integration contract

- [x] 1.1 Add the opt-in pytest integration smoke using only
  `HttpEvidenceProvider` and frozen v1 HTTP endpoints.
- [x] 1.2 Assert evidence/citation identity, provenance, and honest empty or
  partial behavior; register the integration marker.

## 2. Verification and handoff

- [x] 2.1 Run the default backend suite and the opt-in smoke against local
  FinEvidence when available.
- [x] 2.2 Run lint, mypy, compileall, OpenSpec, CodeGraph, Git checks, and
  document the command/result boundary without modifying FinEvidence.
