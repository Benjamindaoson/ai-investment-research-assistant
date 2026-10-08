## Why

The repository currently has a polished but mock-only Next.js research UI and a separate Iowa Liquor enterprise data product on `main`. They are valuable candidates, but together they create competing product identities and no canonical durable Financial DeepResearch Runtime. This change establishes one product line whose research state, evidence provenance, recovery, and evaluation can be verified independently of model output or FinEvidence.

## What Changes

- **BREAKING** Remove `legacy_imports/`, the historical FastAPI/LangGraph/RAG/StockTitan/Stock Monitor/Spring/MCP implementations, course copies, and unrelated demo material.
- Keep `apps/web` as the only frontend and retarget its fixtures and product documentation to financial research.
- Add one `backend/research-runtime` Python package with versioned Pydantic contracts, a durable SQLite store, a deterministic Research Runtime, a FinEvidence provider boundary, FastAPI endpoints, and executable evaluation cases.
- Absorb the reusable ideas from `main` without importing its Iowa Liquor domain, DuckDB pipeline, second Vite frontend, or Figma/agent-tooling artifacts.
- Add an evidence-backed canonical architecture, branch audit, product specification, runtime README, and explicit mock/incomplete capability boundary.

## Capabilities

### New Capabilities

- `research-runtime`: Durable Financial DeepResearch cases, task DAG execution, evidence qualification, claims/thesis synthesis, checkpoint recovery, trace events, and API boundaries.
- `research-evaluation`: Deterministic golden-case evaluation of runtime state, evidence linkage, and abstention behavior.
- `repository-consolidation`: One canonical frontend/backend/runtime structure with explicit deletion and archival policy.

### Modified Capabilities

- None. Existing frontend P0 requirements remain useful as UI behavior, but this change does not silently alter their contract; the frontend is adapted through fixtures and a future-compatible service boundary.

## Impact

- Adds `backend/research-runtime` and its Python dependency environment.
- Removes the legacy and Iowa-specific application trees from the canonical branch.
- Updates root scripts, README, product docs, OpenSpec artifacts, and architecture evidence.
- No FinEvidence implementation, live market-data provider, broker integration, GraphRAG, or production LLM provider is added.
