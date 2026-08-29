# Frontend-first Workspace Foundation Design

## Intent

Create a frontend-only, high-fidelity AI and embodied-intelligence research workspace based on the supplied desktop reference images. It is a product prototype—not a live research system—and all data stays in clearly labelled fixtures.

## Initial delivery

The first build will use a pnpm workspace with `apps/web`, Next.js 16 App Router, strict TypeScript, Tailwind 4, a custom token system, reusable primitive and research components, and a responsive three-column application shell. It will include the Today, New Research, Company Research, Research Case, Research Matrix, Signal Review, and Living Brief routes.

The visual language preserves the references' dark fixed navigation rail, fine neutral borders, compact top bar, controlled blue action color, tabular numerical layout, right-hand evidence context, and dense desktop information architecture. Content is replaced with AI, agent, robotics, and embodied-intelligence research fixtures.

## Architectural boundaries

Routes call TanStack Query hooks, hooks call repositories, and repositories call a typed service interface backed initially by MSW / fixture implementations. Components never fetch APIs directly. Zustand owns UI-only state. This permits replacing services with FastAPI adapters later without screen rewrites.

## Constraints

No backend, database, authentication, RAG, LangGraph, agent runtime, or real-time market feed is part of this delivery. Transitions remain 150–220ms and respect reduced-motion preferences. The desktop shell changes navigation and context panes into drawers on narrow viewports.

## Verification

Vitest and Testing Library cover stateful primitives and mocked research progress; the final loop runs lint, strict typecheck, test, build, and browser smoke checks. The complete OpenSpec contract is at `openspec/changes/frontend-first-workspace-foundation/`.
