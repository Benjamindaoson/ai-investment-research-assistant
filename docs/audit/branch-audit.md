# Branch consolidation audit

Date: 2026-09-13  
Repository: `https://github.com/Benjamindaoson/ai-investment-research-assistant`  
Working branch: `refactor/deepresearch-v2`

## Evidence baseline

| Ref | Commit | Files | Decision |
|---|---|---:|---|
| `master` | `ad7fb2619c4687e7b8777f30b4bda7da0e032243` | 450 | Canonical frontend candidate |
| `origin/main` | `c7307c8` | 257 | Candidate backend concepts; not merged |
| `legacy_imports` on `master` | historical tree | 340 files removed by `main` | Delete from canonical branch |

`main` is not a superset of `master`: it adds an Iowa Liquor `enterprise-data-agent` backend, a Vite/Figma frontend, and removes most legacy imports. The new branch is based on `master`; selected concepts are reimplemented under new ownership rather than merged.

## KEEP

- `apps/web`: strongest current product surface, Next.js 16 App Router, compact research workstation shell, evidence-aware UI, typed Query → Repository → Service boundary, Zod validation, and deterministic interaction tests.
- `apps/web/src/domain/research.ts`: useful frontend boundary vocabulary, to be aligned with the backend contract over time.
- `apps/web/src/repositories`, `apps/web/src/queries`, and `apps/web/src/services`: preserve the replaceable frontend transport direction.
- `docs/product/P0_PRODUCT_SPEC.md`: rewritten as the canonical financial product boundary and workflow specification.

## ABSORB AND REWRITE

- `main` domain model concepts: task state, context/version refs, evidence requirements, tool execution, observations, validation, claims, claim-evidence links, artifacts, events, audit records, checkpoints, and evaluation cases.
- `main` persistence concepts: first-class IDs/state/timestamps plus JSON payload evolution, implemented locally with SQLite for this phase.
- `main` evaluation discipline: golden cases and explicit N/A rather than invented scores.

## DELETE

- `legacy_imports/`: old FastAPI/LangGraph/RAG, StockTitan, stock monitor, Spring Boot, MCP utilities, course copies, and unrelated Iowa/teaching assets. No supported caller exists from the kept application.
- `main`-only `frontend/data-ananlysis-demo`: a second UI/API/type/store system with a typo in its product directory and Enterprise Data/Iowa semantics; it would reintroduce competing frontend ownership.
- `main`-only Iowa Liquor ingestion, curated snapshots, semantic package, and DuckDB analysis: domain-specific implementation not owned by Financial DeepResearch and not a substitute for FinEvidence.
- `.agents`, `.claude`, `.figma`, and design-tool artifacts nested inside the main-only frontend: delivery-process noise, not product runtime.
- Old reports claiming completed or production behavior without a current canonical runtime.

## ARCHIVE

No executable archive is kept in the canonical branch. The source commits remain available in Git history (`master`, `main`, and their ancestors). This is intentional: archive-as-code would recreate the competing product lines the consolidation is meant to remove.

## Resulting ownership

```text
apps/web                       frontend and interaction state
backend/research-runtime       API, runtime, durable state, evidence boundary
backend/research-runtime/...   canonical Python domain contracts
backend/research-runtime/evaluation  executable golden cases/scorer
docs/architecture              source-evidenced architecture
```
