## Context

The first phase established a durable Python runtime and a Next.js research workspace, but the two sides currently meet only conceptually. The runtime's provider protocol accepts typed evidence, while the frontend always uses an in-process synthetic service. FinEvidence must remain an independent evidence infrastructure, so this phase needs a narrow contract that can be implemented by FinEvidence or a local deterministic adapter without importing retrieval or RAG concerns into this repository.

## Goals / Non-Goals

**Goals:**

- Make evidence provenance a first-class, validated part of the runtime contract.
- Provide a small HTTP adapter with timeouts and response validation for a FinEvidence-compatible provider.
- Expose an explicit runtime summary that lets clients trace claims to evidence and task requirements.
- Add a typed frontend HTTP service implementation while preserving the current repository boundary and local synthetic mode.
- Prove the end-to-end path without requiring network access or credentials.

**Non-Goals:**

- Implementing FinEvidence, document parsing, RAG, vector search, market data ingestion, or an LLM planner.
- Replacing SQLite, adding a queue, or introducing authentication and tenancy.
- Rebuilding the frontend or adding new dashboard surfaces.

## Decisions

1. **Version the provider payload explicitly.** The adapter accepts a small `schema_version` plus an array of evidence records. Unknown fields are rejected at the boundary; the runtime's Pydantic models remain the canonical internal representation.

2. **Require provenance for externally supplied evidence.** External records carry source URL, source version, locator, content hash, and retrieval timestamp. The deterministic provider may keep its fixture provenance, but the API must make its non-production identity explicit.

3. **Keep provider transport synchronous and dependency-light.** Use Python's standard-library `urllib` in the HTTP adapter. This avoids adding another HTTP client to a small runtime and keeps tests deterministic. A bounded timeout converts transport failures into an explicit provider error; it never creates synthetic evidence.

4. **Expose a stable run summary rather than leaking storage shape.** The API returns the existing run plus an evidence trace summary. The summary is derived from persisted run state and includes qualification counts, claim evidence IDs, and provenance completeness.

5. **Keep frontend transport selection at repository composition.** `researchRepository` selects the HTTP service only when an explicit environment flag is enabled; otherwise it retains the local synthetic service. Components and hooks remain unchanged.

## Risks / Trade-offs

- [External provider schema drift] → Validate `schema_version` and every record; reject incompatible payloads with a useful error.
- [Network timeout or partial provider failure] → Preserve the runtime failure state and event; do not convert a timeout into a successful task.
- [Frontend API unavailable during local development] → Keep synthetic mode as the default and document the opt-in flag.
- [Provenance fields are incomplete in old fixtures] → Mark fixture provenance explicitly and keep production qualification stricter than demo qualification.

## Migration Plan

1. Add contract fields and provider adapter behind existing interfaces.
2. Add API endpoint and tests using a local fake HTTP server or injected transport.
3. Add frontend HTTP service composition and repository tests.
4. Run existing frontend/backend checks and the new end-to-end contract test.
5. Roll back by disabling the frontend HTTP flag and using the deterministic provider; no database migration is required.

## Open Questions

- FinEvidence's final wire schema and authentication mechanism remain external integration decisions.
- Production deployment may later replace the standard-library transport with a shared client once retry, tracing, and connection pooling requirements are measured.
