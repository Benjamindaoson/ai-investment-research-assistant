## Why

Research teams working on AI and embodied intelligence need a dense, evidence-first workspace rather than disconnected dashboards or a generic chat interface. The supplied reference screens establish a clear desktop research-workflow language that must be adapted into a navigable product prototype before any backend or agent runtime work begins.

## What Changes

- Initialize a pnpm workspace with a strict TypeScript Next.js 16 application at `apps/web`.
- Establish a custom research design system: visual tokens, primitive UI controls, application shell, responsive layout, command palette, interaction states, and accessibility foundations.
- Deliver the complete mock-data-driven P0 flow defined by `docs/product/P0_PRODUCT_SPEC.md`: Today, New Research setup, editable plan, streaming research, Research Case and Findings, Evidence Intelligence, Company Research, Thesis, Risk / Catalyst, What to Monitor, Human Review, Living Brief, Versioning, and a basic Research Library.
- Add backend-replaceable domain schemas and typed operation contracts behind mock service, repository, and query boundaries so a future backend can replace fixtures without page-level coupling.
- Add mocked research progress / streaming states, route loading and error surfaces, and representative tests.

## Capabilities

### New Capabilities
- `research-workspace-shell`: Provides the responsive desktop workspace frame, navigation, global search, command palette, and shared interaction states.
- `research-design-system`: Provides product tokens and reusable UI / research presentation components.
- `today-research-worklist`: Provides the Today research queue and operational summary view.
- `research-analysis-workspaces`: Provides the end-to-end Research Case, findings, evidence, company, thesis, review, brief, versioning, and library workspaces with typed mock research data.

### Modified Capabilities

None.

## Impact

- Adds the `apps/web` Next.js application and pnpm workspace configuration.
- Adds frontend dependencies including Tailwind, Radix primitives, Lucide, TanStack Query/Table/Virtual, Zustand, Motion, React Hook Form, Zod, and MSW.
- No API, database, LangGraph, RAG, agent-runtime, authentication, or live market-data integration is introduced.
