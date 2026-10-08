# Financial DeepResearch Agent

Financial DeepResearch Agent is an evidence-first research operating system for investment analysts. It turns an investment question into a bounded research plan, executes typed research tasks, qualifies evidence, preserves counter-evidence, synthesizes claims and theses, and routes the result through human review before an investment memo is approved.

The active product line is intentionally narrow:

| Area | Active path | Role |
| --- | --- | --- |
| Analyst workspace | `apps/web` | Next.js UI for live research runs, evidence trace, memo, review, and decisions |
| Research runtime | `backend/research-runtime` | FastAPI runtime, durable state, task DAG, evidence boundary, synthesis, memo, review, decisions |
| Product docs | `docs/product`, `openspec` | Current product scope and change specifications |

Historical or separate experiments may still be reachable through Git history. They are not the active application surface and should not receive new feature work unless they are deliberately extracted or reintroduced through a new spec.

## Current architecture

```text
Next.js Research Workspace
  → typed service / repository boundary
  → FastAPI Research Runtime
  → ResearchCase / ResearchPlan / ResearchRun / Task DAG
  → Evidence requirements / FinEvidence-compatible provider boundary
  → Evidence qualification / claim verification
  → Thesis / Memo / IC Review / Human Decision
  → SQLite or PostgreSQL state, append-only events, checkpoints
  → Optional Redis-backed worker dispatch
```

The repository owns the research workflow, state machine, evidence consumption boundary, memo generation, and review/decision workflow. It does not own external financial document ingestion, broad market data, autonomous trading, or investment-advice guarantees.

## Run locally

Install frontend dependencies from the repository root:

```bash
pnpm install
pnpm dev
```

The workspace is available at `http://localhost:3000`.

Run the Research Runtime from `backend/research-runtime`:

```bash
python -m venv .venv
. .venv/bin/activate
python -m pip install -e ".[dev]"
python -m uvicorn deepresearch.asgi:app --reload --port 8010
```

Use `/api/v1/health` for liveness and `/api/v1/ready` for deployment readiness. Readiness checks the engine, store, queue, tools, planner, synthesizer, and runtime reliability layer.

Start the frontend against the runtime:

```bash
NEXT_PUBLIC_RESEARCH_RUNTIME_URL=http://127.0.0.1:8010 pnpm dev
```

Open `http://localhost:3000/new-research` or `/runtime` for the canonical live workflow.

## Docker Compose

Copy `.env.example` to `.env`, then run:

```bash
docker compose up --build
```

Compose starts PostgreSQL, Redis, the runtime, and a worker. The runtime container healthcheck uses `/api/v1/ready`, so it will not be marked healthy if the store, queue, tools, planner, synthesizer, or reliability layer are unavailable.

Use fixture mode by leaving `FIN_EVIDENCE_BASE_URL` blank. Configure `FIN_EVIDENCE_BASE_URL` to connect an external FinEvidence-compatible service.

## Verification

Frontend:

```bash
pnpm lint
pnpm typecheck
pnpm test
pnpm build
```

Backend:

```bash
cd backend/research-runtime
python -m ruff check src tests
python -m mypy src
python -m pytest -q -m "not integration"
```

External-provider, PostgreSQL, Redis, browser E2E, and real LLM checks require separately configured services.

## Reliability status

Already implemented:

- CI for backend ruff, mypy, pytest and frontend lint, typecheck, tests, build.
- Provider evidence IDs separated from runtime evidence IDs.
- External verifier ID canonicalization.
- Financial fact currency and unit-scale guards.
- Frontend runtime cache invalidation after write operations.
- BLOCKED recovery entry points for unknown-effect tool attempts.
- Worker lease-loss isolation.
- Cancelled-run write protection in SQLite and PostgreSQL stores.
- VERIFYING run recovery and claim-verification UNKNOWN_EFFECT blocking.
- Replan invalidation when completed task input hashes drift.
- Atomic final run/event/memory writes for completed and partial runs.
- Readiness endpoint and Docker healthcheck based on deployment readiness.

Still not production-complete:

- fact-level numeric verification from source evidence;
- identity and access control for multi-user review;
- full browser E2E over the live runtime;
- complete removal of inactive historical enterprise analytics directories, currently retained only as historical artifacts until deletion can be safely applied.
