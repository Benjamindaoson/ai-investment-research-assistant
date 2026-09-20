# Atlas Research Workspace

**Evidence-first AI & Embodied Intelligence Research OS**

This repository is a research-workspace product for professional AI / robotics industry research. It is intentionally distinct from `Financial_Asset_QA_System`.

## Product role

```text
Research Question
    ↓
Research Case
    ↓
Research Plan
    ↓
Multi-source Research
    ↓
Evidence / Counter-Evidence
    ↓
Findings
    ↓
Thesis
    ↓
Human Review
    ↓
Living Brief + Versioning
```

The product is designed for:

- AI / robotics industry research;
- VC / PE / strategic research workflows;
- evidence and counter-evidence management;
- thesis tracking and versioning;
- human-reviewed living research outputs.

## Not the same as Financial Asset QA

| Repository | Primary role |
| --- | --- |
| `Financial_Asset_QA_System` | Financial QA / market-data tool execution / deterministic validation / guarded answer synthesis |
| `ai-investment-research-assistant` | Evidence-first research OS for companies, industries, technologies, claims, counter-evidence and living theses |

These repositories should remain separate unless their product boundaries materially converge.

## Current implementation status

The current implementation is **frontend-first** and uses explicit mock/service boundaries while product semantics and information architecture are stabilized.

Current stack:

- Next.js / React / TypeScript
- TanStack Query
- Zustand
- Zod
- MSW
- Vitest / Testing Library

Backend / RAG / agent runtime work is intentionally deferred until authorized by the product spec.

## Source of truth

See:

- `docs/product/P0_PRODUCT_SPEC.md`
- `AGENTS.md`
- active OpenSpec changes under `openspec/`

## Historical consolidation

Earlier investment-research prototypes are preserved under `legacy_imports/`.

See `docs/repository-consolidation-2026-09-10.md`.

## Portfolio status

**Product incubator / research workspace**, not a current public flagship.
