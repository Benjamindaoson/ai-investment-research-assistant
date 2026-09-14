## 1. Provider implementation

- [x] 1.1 Refactor shared HTTP evidence conversion and add
  `HttpTableEvidenceProvider` using `/api/v1/table/query`.
- [x] 1.2 Export the provider and register `financial-table` for real
  FinEvidence app configuration without changing explicit registries.

## 2. Verification

- [x] 2.1 Add unit tests for table routing, slot propagation, citation identity,
  empty results, and unchanged search behavior.
- [x] 2.2 Extend the opt-in real smoke, run backend/frontend checks, OpenSpec,
  CodeGraph, HTTP smoke, and Git checks; update docs.
