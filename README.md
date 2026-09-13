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
  → Claims / Evidence-grounded Thesis / Memo / Human Decision
  → Investment Memory / Financial Analysis
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

To use the connected runtime workspace, start the backend first, configure its
allowed browser origin, and start Next.js with the runtime URL:

```powershell
# Terminal 1, from backend/research-runtime
Set-Location backend/research-runtime
$env:RESEARCH_RUNTIME_CORS_ORIGINS = "http://localhost:3000"
.\.venv\Scripts\python -m uvicorn deepresearch.api:app --reload --port 8000

# Terminal 2, from the repository root
Set-Location ../..
$env:NEXT_PUBLIC_RESEARCH_RUNTIME_URL = "http://127.0.0.1:8000"
pnpm dev
```

Open `http://localhost:3000/runtime` for the live case/run workflow. Without
the runtime URL, the existing design workspace stays explicitly synthetic.

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

Implemented: typed domain contracts, deterministic and opt-in structured LLM
planner boundaries, validated ResearchPlan provenance, DAG validation, durable
SQLite state, append-only events, checkpoints, resumable execution, explicit
cancellation, evidence qualification, evidence-grounded claim/thesis
synthesis, durable investment memos with structured evidence-linked review
sections, target-level Investment Memory with observed ThesisDelta and run-scoped
memory reads, Decimal financial analysis, decision endpoints, typed
Next.js runtime transport, live runtime workspace, and an honest evaluation
scorer.

Incomplete by design: FinEvidence production deployment, live filing and market
providers, LLM plan quality promotion, PostgreSQL, authentication, document
parsing, monitoring triggers, rich memo export, and trading execution. No output
should be interpreted as investment advice.

The runtime transport can be enabled for an external-compatible provider with
`NEXT_PUBLIC_RESEARCH_RUNTIME_URL`; without it, the workspace remains in its
explicit synthetic-data mode.

Planner quality is evaluated independently from execution quality. The local
evaluation command reports plan coverage, dependency edges, evidence
requirements, counter-evidence coverage, task ceiling, and duplicate-task
checks separately from the executed run checks. The opt-in LLM planner has
passed transport and runtime contract preflights, but its output has not yet
beaten the deterministic baseline on the authored golden case and therefore is
not the default planner.

The branch audit and selection record is in
[`docs/audit/branch-audit.md`](docs/audit/branch-audit.md); the source-evidence
architecture artifact is in `docs/architecture/`.
