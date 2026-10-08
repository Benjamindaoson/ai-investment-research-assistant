## Context

The backend already persists the research run and exposes each downstream artifact as a separate typed operation. The missing MVP seam is orchestration: a single local invocation must make the order and validation rules explicit while preserving the existing SQLite event log and artifact write paths. The implementation must work with the deterministic provider on one computer and must also work when the same run has been populated through the HTTP FinEvidence provider.

## Goals / Non-Goals

**Goals:**

- Provide one typed endpoint for a complete local MVP workflow.
- Reuse the existing engine, financial calculator, valuation calculator, review validation, decision validation, and evaluation scorer.
- Execute a created or queued run before accepting downstream artifacts.
- Keep all analyst inputs explicit: typed facts, evidence IDs, review rationales, and decision rationale.
- Return a compact receipt that makes the complete workflow observable.

**Non-Goals:**

- No new agent loop, RAG implementation, database, queue service, auth, or production deployment.
- No automatic extraction of financial numbers from evidence excerpts.
- No automatic approval or fabricated review content.
- No changes to the FinEvidence repository or its API contract.

## Decisions

1. Add a small `runtime.mvp` orchestration function and a `POST /api/v1/research-runs/{run_id}/mvp-complete` route. The function will call existing engine methods in a fixed order so validation and event persistence remain centralized. A new service abstraction or separate database is unnecessary for the single-machine MVP.

2. The request will contain `FinancialFactSet`, `ScenarioValuationInput`, one red-team review seed, exactly one IC review for each of `BULL`, `BEAR`, `FINANCIAL`, `INDUSTRY`, and `PARTNER`, a decision, and no free-form evaluation contract. The server builds the canonical MVP evaluation case from the run and checks all five roles.

3. If the run is `CREATED` or `PARTIAL`, the endpoint executes it synchronously with the existing lease/checkpoint semantics. If execution remains non-complete, the workflow stops before writing downstream artifacts. A separate enqueue/worker path remains available for long-running local runs.

4. The endpoint constructs review and decision domain objects only after the run thesis exists, attaching the current run and thesis IDs. It records each artifact through the existing methods, so evidence qualification and target ownership cannot be bypassed.

5. The response is a receipt rather than the entire run document: run/case IDs, terminal state, memo status, artifact IDs/input hashes, review IDs, decision IDs, and the persisted evaluation result. This keeps the API usable while all details remain available through existing GET endpoints.

## Risks / Trade-offs

- [Synchronous execution can block an HTTP request] → This is intentionally a local MVP path; the existing enqueue plus worker commands remain the durable option for long runs.
- [The workflow is not a database transaction across several artifact writes] → Every step is persisted as an event and failed retries return the failing validation; production transactional orchestration is explicitly out of scope.
- [The valuation calculator is illustrative rather than a full DCF] → Preserve its existing provenance flag and label it in documentation; do not present it as production valuation.
- [A five-role review requirement is stricter than the individual review endpoint] → It applies only to the complete MVP endpoint; individual review APIs remain useful for incremental work.
