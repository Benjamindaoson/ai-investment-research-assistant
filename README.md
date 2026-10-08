# Financial DeepResearch Agent

An evidence-first research operating system for investment analysts. The
canonical product line is a Next.js research workspace backed by a small,
durable Python Research Runtime. It plans research, executes typed tasks,
qualifies evidence, synthesizes claims and theses, preserves counter-evidence,
and records structured IC reviews plus human decisions. The Atlas workspace
also preserves its original focus on AI, robotics, and strategic research
workflows: evidence before prose, with human judgment before a final decision.

## Repository and product boundaries

`master` is the consolidated development branch. The default product is
Financial DeepResearch; the independent Enterprise Intelligence Workspace
implementation from the former `main` branch is also preserved in this tree.

| Location | Role | How it is used |
| --- | --- | --- |
| [`apps/web`](apps/web) | Atlas / DeepResearch Next.js workspace | Root `pnpm dev`, `build`, and test commands |
| [`backend/research-runtime`](backend/research-runtime) | Durable investment research API and worker | Default research backend; root Compose |
| [`backend/enterprise-data-agent`](backend/enterprise-data-agent) | Independent Iowa / enterprise structured-data analysis implementation | Run from its own directory using its README |
| [`frontend/data-ananlysis-demo`](frontend/data-ananlysis-demo) | Independent Vite frontend for the enterprise API | Install and run separately from its own directory |
| [`DESIGN.md`](DESIGN.md) | Historical enterprise-workspace design | Reference material; current research spec is under `docs/product` |

The enterprise projects keep their own packages, dependencies, APIs, and
startup commands. The root pnpm workspace still includes only `apps/*`.
When running independent services together, check their configured ports:
the enterprise API and the FinEvidence example both use port 8000, and both
Compose stacks use PostgreSQL port 5432 by default.

This repository owns research workflow, execution, evidence/counter-evidence,
theses, and human review. `Financial_Asset_QA_System` owns its separate
financial-question-answering and market-data-tool workflow. FinEvidence owns
external evidence infrastructure. Consolidating this repository's branches
does not combine those separate repositories or responsibilities.

See the [branch consolidation record](docs/repository-consolidation-2026-10-08.md)
for the original branch tips, conflict decisions, and historical README links.

This repository does not reimplement FinEvidence. FinEvidence is the
external evidence infrastructure; this project consumes it through an explicit
`EvidenceProvider` boundary.

Research tasks resolve their declared `tool_name` through an explicit
`ResearchToolRegistry`; unknown tools fail durably instead of falling back to a
global provider. Qualification and claim verification use the provider selected
for the task.

Evidence requirements preserve FinEvidence-aligned fact type, role, criticality,
evidence role, and financial/source slots from the research plan through the
coverage request; missing values remain missing rather than being inferred.
Real FinEvidence configuration also exposes the registered `financial-table`
data tool for exact entity/metric/period candidate evidence; it does not infer
financial values or bypass the existing qualification gate.

## Canonical architecture

```text
Next.js Research Workspace
  → typed service / repository boundary
  → FastAPI Research Runtime
  → ResearchCase / ResearchPlan / ResearchRun / Task DAG
→ Evidence Requirements / FinEvidence v1 HTTP Client
  → Partial Coverage / Durable Replanning
  → Claims / Evidence-grounded Thesis / IC Review Panel / Memo / Human Decision
  → Investment Memory / Financial Analysis
  → PostgreSQL events + checkpoints / Evaluation
  → Redis dispatch
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

The canonical research routes use the connected Research Runtime. Other
workspace demonstrations retain explicitly labelled synthetic fixtures. The
backend has a deterministic local provider so the durable runtime and review
semantics can be exercised without external credentials or live market data.
When canonical `FIN_EVIDENCE_BASE_URL` is set, the runtime uses the frozen FinEvidence
Evidence Backend v1 contract: search → requirement coverage → citation. This
repository does not import FinEvidence retrieval, parser, table IR, eval, or
CLIP modules, and it does not silently fall back when the external service
fails. The legacy `FINEVIDENCE_BASE_URL` name remains a compatibility alias.

## Product tour

With the runtime and frontend configured as described below:

1. Open **New Research** (`/new-research` or `/runtime`) and create a research
   case with an explicit question and target.
2. Inspect the plan, typed tasks, evidence requirements, and execution trace.
3. Review qualified evidence, counter-evidence, claim verification, and the
   resulting thesis; keep missing coverage and uncertainty visible.
4. Record structured IC review and a human decision, then inspect the memo and
   case/run history. Review scenario assumptions and evidence links before
   using financial-analysis artifacts.

The value of this workflow is an inspectable research process and reusable
research output. Live source quality and planner quality still require their
own evaluation; a completed run is not proof that an investment conclusion is
correct.

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
# Terminal 1, from FinEvidence (optional external service)
Set-Location "D:\01_work\Enterprise Multimodal RAG\finevidence"
\.venv\Scripts\python.exe -m uvicorn finevidence.api.app:app --host 127.0.0.1 --port 8000

# Terminal 2, from backend/research-runtime
Set-Location backend/research-runtime
$env:FIN_EVIDENCE_BASE_URL = "http://127.0.0.1:8000" # use FinEvidence v1
$env:RESEARCH_RUNTIME_CORS_ORIGINS = "http://localhost:3000"
.\.venv\Scripts\python -m uvicorn deepresearch.api:app --reload --port 8010

# Terminal 3, from the repository root
Set-Location ../..
$env:NEXT_PUBLIC_RESEARCH_RUNTIME_URL = "http://127.0.0.1:8010"
pnpm dev
```

Open `http://localhost:3000/new-research` (or `/runtime`) for the canonical live
case/run workflow. The old `/research` entry point now redirects there, and
`/research/{caseId}` resolves the latest durable run. Without the runtime URL,
the page shows an explicit configuration error instead of presenting fixture
output as live research.

Run the backend from `backend/research-runtime`:

```powershell
python -m venv .venv
.\.venv\Scripts\python -m pip install -e ".[dev]"
.\.venv\Scripts\python -m uvicorn deepresearch.api:app --reload --port 8010
```

Health endpoint: `http://127.0.0.1:8010/api/v1/health`.

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
synthesis, durable uniquely identified research runs with case-scoped history,
investment memos with structured evidence-linked review
sections, target-level Investment Memory with observed ThesisDelta and run-scoped
memory reads, Decimal financial analysis, durable run-scoped financial analysis
artifacts that require field-level links to qualified evidence already present
in the same run, decision endpoints, typed
Next.js runtime transport, live runtime workspace, case-scoped reruns, durable
requirement-driven replanning, external claim verification gating, and an
honest evaluation scorer.

Structured Bull/Base/Bear valuation scenarios are also available as an
explicit, evidence-linked illustrative terminal-value artifact; they do not
fetch prices or create investment advice.

Incomplete by design: live filing and market providers, LLM plan quality
promotion, authentication, document parsing, monitoring triggers,
rich memo export, and trading execution. FinEvidence remains an independent
service; its deployment, retrieval, provenance, and evidence qualification are
outside this repository. No output should be interpreted as investment advice.

`NEXT_PUBLIC_RESEARCH_RUNTIME_URL` selects the connected Research Runtime.
Without it, canonical research routes show an explicit configuration error;
they do not silently substitute synthetic research results.

The live run page polls active durable state and trace data every two seconds,
then stops at terminal outcomes. This is bounded read-back of the runtime's
checkpoint/lease state, not a claim of background execution or exactly-once
provider work.

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
