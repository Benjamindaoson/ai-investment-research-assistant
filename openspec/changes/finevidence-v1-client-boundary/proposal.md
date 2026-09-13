## Why

The runtime still points its HTTP evidence provider at the retired
`/v1/evidence/collect` payload. That endpoint is not FinEvidence Evidence
Backend v1, so configuring `FINEVIDENCE_BASE_URL` currently cannot execute the
product's real evidence boundary.

## What Changes

- Replace the retired collect payload with a typed, standard-library HTTP
  client for the frozen FinEvidence v1 endpoints.
- Execute the narrow production path `search -> coverage -> citation` for each
  research task and preserve FinEvidence qualification as the external source
  of truth.
- Convert the versioned FinEvidence evidence object into the runtime's
  `EvidenceRecord` without importing FinEvidence implementation modules.
- Keep the deterministic provider explicitly local and synthetic for tests and
  offline development.
- Add contract tests for request routing, response validation, qualification
  propagation, citation provenance, and transport failures.

## Non-goals

- No changes to the FinEvidence repository.
- No local retrieval, RAG, parsing, table IR, benchmark, or CLIP code.
- No live-market provider, authentication system, retry queue, or database
  migration.

## Impact

- `backend/research-runtime/src/deepresearch/runtime/evidence.py` becomes the
  only integration boundary.
- Runtime qualification no longer promotes an externally rejected or partial
  FinEvidence result locally.
- Existing deterministic runtime tests remain offline and unchanged in intent.
