## Context

The repository is newly initialized and contains reference screenshots only. The product is an evidence-first AI and embodied-intelligence research workspace. The first release is a frontend-only product prototype: all data is intentional mock data and no database, server API, agent runtime, LangGraph, RAG, or authentication is in scope.

The supplied screens establish the design language: a fixed dark navigation rail, white global header, dense structured workspace, restrained blue action color, subtle borders, compact data tables, and an optional right-hand context pane. The product adapts this language to research questions about AI, agents, robotics, and embodied intelligence without copying the reference brand or financial copy.

## Goals / Non-Goals

**Goals:**
- Produce a navigable Next.js 16 prototype under `apps/web` with custom visual tokens and reusable domain components.
- Make each supplied research workflow available as a typed, mock-data-driven route with practical loading, empty, error, selected, and streaming states.
- Use a service/repository/query boundary and local MSW handlers so a future FastAPI endpoint can replace fixtures without changing screens.
- Maintain responsive and keyboard-accessible behavior while preserving a desktop-first high-information-density layout.

**Non-Goals:**
- Implementing any backend, data persistence, live search, market feed, exported documents, user management, RAG, LangGraph, or agent runtime.
- Copying third-party logos, trademarks, or supplied Chinese-language financial content.
- Building all potential workspace pages beyond the supplied reference workflows and the New Research entry point.

## Decisions

### Next.js workspace application
Use a pnpm workspace with `apps/web` as a Next.js App Router application. This keeps the current frontend isolated and permits future API, shared types, or packages without a relocation. App Router route-level `loading.tsx` and `error.tsx` supply the base async experience.

Alternative: use a single root Next.js application. Rejected because the requested structure explicitly anticipates `apps/web` and a workspace does not materially increase the client bundle.

### Custom token-first component system
Define CSS custom properties for color, typography, spacing, radius, shadows, borders, surfaces, motion, density, and focus / hover / selected states in `styles/tokens.css`. Tailwind consumes the CSS variables. Primitives in `components/ui` use CVA, Radix where interaction semantics matter, and Lucide icons; domain components sit in `components/research`, `components/evidence`, and `components/thesis`.

Alternative: adopt a stock shadcn theme. Rejected because it would conflict with the provided reference's compact, institutional hierarchy and the explicit custom design-system requirement.

### Typed mock boundary
Page components call hooks in `queries/`, which call repositories. Repositories receive a typed service interface with MSW-backed handlers and fixtures under `lib/mock`. The initial app has no page-level `fetch` calls. Zustand owns cross-route UI state such as context-pane visibility and command palette state; TanStack Query owns async mock server state.

Alternative: import fixtures directly into pages. Rejected because it cannot be swapped to FastAPI cleanly and makes loading/error states artificial.

### Dense responsive shell
Desktop widths render a 224px navigation rail, 56px top bar, flexible main column, and optional 320px context pane. At tablet widths, the context pane moves to an overlay drawer; at phone widths, navigation becomes a drawer and tables retain only critical columns. Split panes have min/max sizes and use CSS grid rather than continuous layout JS.

### Streaming research simulation
The research run repository returns a stream of named stages with timed fixture events. A client `ResearchProgress` progressively appends events and reveals findings. The simulation is explicitly labelled as a prototype and is cancellable / restartable in client state.

## Risks / Trade-offs

- [Reference screens are large, desktop-only images] → Preserve their density on desktop and introduce measured breakpoints without pretending the screenshots define mobile behavior.
- [Mock results can be mistaken for live research] → Label sample status and locate all fixture data under `lib/mock/fixtures`.
- [Rich design system could overgrow the first release] → Only add primitives used by the reference workflows; defer editors, PDFs, graph visualization, Storybook, and advanced virtualisation to later change sets.
- [Animation can reduce institutional feel] → Limit transforms and opacity transitions to 150–220ms, respecting `prefers-reduced-motion`.

## Migration Plan

1. Bootstrap the workspace and establish token / component contracts.
2. Implement routes exclusively through typed mock repositories and validate the prototype locally.
3. When the backend phase begins, replace MSW handlers with FastAPI service implementations while retaining repository interfaces and query hooks.
4. If a new frontend deployment is unsuccessful, revert to the prior static deployment because this release introduces no data migration or persistent state.

## Open Questions

- The supplied screenshots do not define mobile behavior; this implementation will use the responsive behavior documented above until a mobile reference is provided.
- Company brand marks will be represented as typographic or geometric placeholders unless the user supplies licensed assets.
