# Financial DeepResearch Agent

Financial DeepResearch Agent is an evidence-first research operating system for investment analysts. It turns an investment question into a bounded research plan, executes typed research tasks, qualifies evidence, preserves counter-evidence, synthesizes claims and theses, and routes the result through human review before an investment memo is approved.

The active product line is now intentionally narrow:

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
python -m uvicorn deepresearch.api:app --reload --port 8010
```

Start the frontend against the runtime:

```bash
NEXT_PUBLIC_RESEARCH_RUNTIME_URL=http://127.0.0.1:8010 pnpm dev
```

Open `http://localhost:3000/new-research` or `/runtime` for the canonical live workflow.

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
python -m pytest -q
python -m deepresearch.evaluation
```

External-provider, PostgreSQL, Redis, browser E2E, and real LLM checks require separately configured services.

## Current limitations

The runtime has useful durable-execution foundations, but several correctness areas still require hardening before the project should be presented as a production-grade investment analyst system:

- cancellation and in-flight worker race handling;
- replanning invalidation when a task's semantic contract changes;
- VERIFYING-stage recovery;
- atomic run/event/memory writes;
- fact-level numeric verification from source evidence;
- identity and access control for multi-user review;
- CI covering backend, frontend, and key runtime regressions.

Recent remediation already added separate provider evidence IDs, external-verifier ID canonicalization, financial fact currency/unit guards, and frontend runtime-flow cache fixes. Continue the modernization by fixing state-machine durability before adding new agent roles or dashboards.
