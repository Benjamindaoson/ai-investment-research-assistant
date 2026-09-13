# Financial DeepResearch Agent

An evidence-first research operating system for investment analysts. The
canonical product line is a Next.js research workspace backed by a small,
durable Python Research Runtime. It plans research, executes typed tasks,
qualifies evidence, synthesizes claims and theses, preserves counter-evidence,
and records human decisions.

This repository does not reimplement FinEvidence. FinEvidence is the future
external evidence infrastructure; this project consumes it through an explicit
`EvidenceProvider` boundary.

## Canonical architecture

```text
Next.js Research Workspace
  → typed service / repository boundary
  → FastAPI Research Runtime
  → ResearchCase / ResearchPlan / ResearchRun / Task DAG
  → Evidence Requirements / FinEvidence Provider
  → Claims / Thesis / Bull-Base-Bear / Decision
  → SQLite events + checkpoints / Evaluation
```

## Product wedge

For a top-tier investment bank, this product is not a replacement for
Bloomberg, FactSet, Capital IQ, internal data platforms, or an existing
research-management system. Its value is a controlled research execution
layer: task contracts, evidence requirements, provenance, counter-evidence,
checkpoint/recovery, and human approval that can sit above those systems and
leave an auditable trail for every investment conclusion.

For an individual investor, the value is different: a focused research
workflow that makes source quality, uncertainty, disconfirming evidence, and
scenario assumptions visible. It earns a place only when it saves substantial
research time and produces a memo the investor can re-check later; a generic
chatbot with a stock ticker is not enough.

The first commercial wedge is therefore the evidence-backed research memo,
not autonomous trading or a broad financial super-app.

The frontend currently uses explicitly labelled synthetic fixtures. The
backend has a deterministic local provider so the durable runtime and review
semantics can be exercised without external credentials or live market data.

## Run locally

Install JavaScript dependencies from the repository root:

```powershell
pnpm install
pnpm dev
```

The workspace is available at `http://localhost:3000`.

Run the backend from `backend/research-runtime`:

```powershell
python -m venv .venv
.\.venv\Scripts\python -m pip install -e ".[dev]"
.\.venv\Scripts\python -m uvicorn deepresearch.api:app --reload --port 8000
```

Health endpoint: `http://127.0.0.1:8000/api/v1/health`.

## Verification

```powershell
# Frontend, from the repository root
pnpm lint
pnpm typecheck
pnpm test
pnpm build

# Backend, from backend/research-runtime
.\.venv\Scripts\ruff check src tests
.\.venv\Scripts\mypy src
.\.venv\Scripts\python -m pytest -q
.\.venv\Scripts\python -m deepresearch.evaluation
```

## Scope and limitations

Implemented: typed domain contracts, deterministic planner boundary, validated
ResearchPlan provenance, DAG validation, durable SQLite state,
append-only events, checkpoints, resume without duplicate completed work,
evidence qualification, claim/thesis synthesis, decision endpoints, and an
honest evaluation scorer.

Incomplete by design: FinEvidence production integration, live filing and
market providers, LLM planning, PostgreSQL, authentication, document parsing,
and trading execution. No output should be interpreted as investment advice.

The runtime transport can be enabled for an external-compatible provider with
`NEXT_PUBLIC_RESEARCH_RUNTIME_URL`; without it, the workspace remains in its
explicit synthetic-data mode.

The branch audit and selection record is in
[`docs/audit/branch-audit.md`](docs/audit/branch-audit.md); the source-evidence
architecture artifact is in `docs/architecture/`.
