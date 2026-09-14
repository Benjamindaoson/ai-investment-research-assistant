## Context

The backend already exposes typed endpoints for ResearchCases, ResearchRuns, planning, enqueue/execute, trace, evidence, claims, thesis, memo, and evaluation. The frontend has a complete `ResearchRuntimeRepository` and runtime workspace, while the older `/new-research` and `/research/[caseId]` routes still point to a fixture-only repository.

## Goals / Non-Goals

**Goals:**

- Make the existing runtime workspace the product's canonical research entry point.
- Keep page components behind TanStack Query and the typed repository/service boundary.
- Support both synchronous local execution and Redis worker enqueue from the same browser workflow.
- Preserve backend-owned evidence qualification and memo state; the browser only renders it.

**Non-Goals:**

- Rebuilding the legacy mock workspaces in this change.
- Adding another frontend state store, browser database, or retrieval implementation.
- Changing FinEvidence APIs or importing FinEvidence internals.

## Decisions

- `/new-research` renders `RuntimeStartWorkspace`; the existing form already captures target, question, and mandate and calls the canonical runtime API.
- `/research` redirects to `/runtime`, and `/research/[caseId]` resolves the latest durable run before navigating to `/runtime/[runId]`. This preserves old links while eliminating the misleading mock execution path.
- The runtime service remains the only frontend transport boundary. Runtime responses continue to be parsed with Zod before rendering.
- A small `apps/web/.env.example` documents the local API URL. The frontend does not silently fabricate a live runtime when the variable is absent.
- Browser verification starts the backend with PostgreSQL/Redis configuration and validates visible case creation, run control, evidence, and memo output.

## Risks / Trade-offs

- [Legacy links may point to fixture case IDs] → The case bridge shows a clear not-found state; new links use durable runtime IDs.
- [A synchronous browser request can block during a long run] → The workspace retains Redis enqueue and two-second polling; local MVP users can choose either start mode.
- [Docker Hub availability can block full-stack verification] → Keep a separately verifiable local API/worker path and report the external image pull blocker explicitly.
