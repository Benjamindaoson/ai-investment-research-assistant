## Context

`master` contains the strongest current product surface: a Next.js 16 workspace with typed Zod boundaries, repository/service separation, evidence-aware screens, review actions, and a complete deterministic UI flow. `main` contributes useful framework-independent contracts and persistence/evaluation concepts, but its concrete implementation is an Iowa Liquor analytical product with a competing Vite frontend and data pipeline. `legacy_imports` is historical material, not a supported runtime.

The target is a financial research operating system, not a generic chatbot or a collection of agents. FinEvidence remains an independent evidence infrastructure and is consumed through a narrow provider contract.

## Goals / Non-Goals

**Goals:**

- Define one canonical domain model for `ResearchCase`, `ResearchRun`, `ResearchTask`, `EvidenceRequirement`, `EvidenceRecord`, `Claim`, `Thesis`, `DecisionRecord`, `ToolExecution`, `Checkpoint`, and `EvaluationResult`.
- Make task dependencies, state transitions, evidence qualification, and recovery deterministic and testable.
- Persist state and append-only events with SQLite and atomic checkpoint writes, without requiring PostgreSQL for local verification.
- Expose a small FastAPI API that the existing frontend service boundary can replace its fixtures with later.
- Prove a complete local vertical slice using deterministic provider data and golden evaluation cases.

**Non-Goals:**

- Reimplementing FinEvidence, RAG, document extraction, live market feeds, broker actions, GraphRAG, Neo4j, MCP swarm orchestration, Kubernetes, or enterprise IAM.
- Preserving old code for historical reasons.
- Rebuilding the existing frontend shell or adding dashboard pages unrelated to the runtime vertical slice.

## Decisions

### 1. SQLite first, SQLAlchemy later

Use the Python standard-library `sqlite3` module for the local durable adapter. The main branch's database tables showed the right durable entities but added no value for this phase when there is no production database deployment. SQLite provides transactions, a single local file, and a realistic read-back path. A future PostgreSQL adapter can implement the same store contract.

### 2. Explicit state machine and DAG, no agent swarm

The runtime accepts a validated task DAG, executes ready tasks once, records tool executions and evidence, then qualifies claims. It never treats a model response as completion evidence. Dynamic replanning is represented as a new plan version/event, not hidden mutation of the active plan.

### 3. FinEvidence provider boundary

`EvidenceProvider` is a small protocol returning `EvidenceRecord` values with source identity, retrieval timestamp, provenance, and qualification status. The local provider is deterministic and marked as demo data. The production provider is intentionally absent until FinEvidence supplies its API contract.

### 4. Evaluation is a scorer, not a dashboard

Evaluation cases are JSON so the first phase has no YAML dependency. The scorer checks terminal state, required evidence, claim links, and abstention. It reports `N/A` for cases whose required external capability is unavailable rather than inventing scores.

### 5. Preserve frontend boundary

`apps/web` remains Page/Component → Query → Repository → Service. The first backend integration adds no direct fixture imports to pages and no frontend rewrite. Existing UI mock behavior stays visibly deterministic until an API adapter is implemented.

## Risks / Trade-offs

- [Local SQLite is not a multi-process production store] → Keep its interface small and document a PostgreSQL adapter as the next persistence phase.
- [Deterministic evidence is not live market evidence] → Label it in API responses, fixtures, and UI; never present it as current investment research.
- [The current frontend still has broader P0 mock screens than the backend] → Treat the backend vertical slice and frontend prototype as separate verified surfaces until their typed API adapter is added.
- [Deleting legacy material removes convenient examples] → Preserve only the audit decision and source commit references; do not keep executable duplicates.

## Migration Plan

1. Create and validate this change on `refactor/deepresearch-v2`.
2. Add the new runtime and tests.
3. Update frontend sample semantics and root documentation.
4. Delete the explicitly rejected trees.
5. Run backend and frontend verification, then record the final Git state.
6. Rollback is a branch deletion or revert; no database migration is required because the new SQLite file is local and ignored.

## Open Questions

- FinEvidence's production request/response contract and authentication are intentionally deferred to the integration phase.
- The first live financial data adapter should be selected after the runtime contracts and evaluation gate remain stable.
