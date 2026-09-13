## Why

The current runtime proves durable task execution with synthetic evidence, but it does not yet expose a production-shaped evidence contract or connect the research workspace to the runtime. That gap prevents the product from proving its core value: a financial research conclusion that can be traced from a question to qualified source evidence and a reviewable decision.

This is the highest-leverage next step for both target users. An investment bank needs a replaceable, auditable research execution boundary that can sit beside its proprietary data stack; an individual investor needs a trustworthy workflow that makes source quality and uncertainty visible instead of presenting unsupported AI prose.

## What Changes

- Add a versioned EvidenceProvider boundary with provenance, source identity, locators, hashes, retrieval time, and explicit qualification outcomes.
- Add a deterministic HTTP evidence provider adapter that can consume a FinEvidence-compatible endpoint without coupling the runtime to FinEvidence implementation details.
- Add runtime API contracts for evidence-backed task execution and traceable claims.
- Add a typed frontend HTTP service implementation behind the existing repository boundary, with an explicit local synthetic fallback.
- Add an end-to-end contract test covering question → task execution → evidence qualification → claim trace.
- Document the product wedge and the hard boundary between this project and FinEvidence.

## Capabilities

### New Capabilities

- `evidence-provider-boundary`: Versioned, provenance-preserving evidence consumption and qualification.
- `runtime-http-transport`: Typed HTTP transport for connecting the research workspace to the Research Runtime.
- `evidence-backed-research-flow`: End-to-end execution and traceability from research question to claim.

### Modified Capabilities

None.

## Impact

- Affected backend: `backend/research-runtime/src/deepresearch/domain`, `runtime`, `api`, and tests.
- Affected frontend: `apps/web/src/services`, `repositories`, queries, and integration tests.
- Affected documentation: root README, product spec, and architecture notes.
- No new database, queue, authentication system, live-market provider, or RAG implementation is introduced in this change.
- The external FinEvidence service remains optional; local tests must run without credentials or network access.
