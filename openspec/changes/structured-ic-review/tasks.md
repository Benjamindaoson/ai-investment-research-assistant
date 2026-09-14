## 1. Domain and API

- [x] 1.1 Add `InvestmentCommitteeReview` and backward-compatible run/decision
  fields with validation enums.
- [x] 1.2 Implement engine ownership validation, append-only event recording,
  listing, and decision review-ID validation.
- [x] 1.3 Expose POST/GET `/api/v1/research-runs/{run_id}/ic-reviews` and
  additive decision request fields.

## 2. Frontend panel

- [x] 2.1 Add Zod schemas, service/repository methods, and query mutation for
  IC reviews.
- [x] 2.2 Add a compact role review form and run workspace panel showing role
  coverage and evidence qualification.
- [x] 2.3 Keep red-team and synthetic behavior backward-compatible.

## 3. Verification

- [x] 3.1 Add backend model, engine, API, persistence, and decision-link tests.
- [x] 3.2 Add frontend service/query/component tests for coverage, invalid
  input, and read-back.
- [x] 3.3 Update documentation and run backend/frontend checks, OpenSpec,
  CodeGraph, diff, API, and browser smoke verification.
