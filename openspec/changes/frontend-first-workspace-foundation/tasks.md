## 1. Workspace foundation

- [x] 1.1 Initialize the pnpm workspace and strict Next.js 16 application in `apps/web` with lint, typecheck, test, and build commands.
- [x] 1.2 Add the frontend dependencies and configuration for Tailwind 4, Radix primitives, CVA, Lucide, TanStack Query/Table/Virtual, Zustand, Motion, React Hook Form, Zod, MSW, Vitest, and React Testing Library.
- [x] 1.3 Define Geist typography and product design tokens for surfaces, borders, motion, density, interaction states, and responsive breakpoints.

## 2. Shared application system

- [ ] 2.1 Implement accessible primitive controls and research-domain presentation components using the token system.
- [x] 2.2 Implement the responsive App Shell with top bar, navigation rail, context pane / drawer, route loading and error boundaries.
- [x] 2.3 Implement Cmd/Ctrl+K command palette and keyboard-accessible navigation actions.

## 3. Mock research boundary

- [x] 3.1 Define shared research, company, evidence, thesis, and activity types and realistic AI / embodied-intelligence fixtures.
- [x] 3.2 Implement typed mock services, repository interfaces, TanStack Query hooks, MSW handlers, and Zustand UI state.
- [x] 3.3 Add tests for mock service contracts, research progress sequencing, and command-palette state.

## 4. Today and New Research

- [x] 4.1 Implement the Today research worklist and operational context pane using the first supplied reference's layout and density.
- [ ] 4.2 Implement the New Research input workflow with validation, attachment mock state, and handoff to a Research Case.
- [ ] 4.3 Add responsive and interaction tests for the Today navigation and New Research submission.

## 5. Research workflow screens

- [ ] 5.1 Implement Company Research with thesis, recent change, evidence detail context, and mocked charts / signals.
- [ ] 5.2 Implement Research Case with plan tree, progressive streaming status, findings, evidence review context, and restart / cancel interactions.
- [ ] 5.3 Implement Research Matrix, Signal Review, and Living Brief screens from the supplied references with adapted research-domain mock content.
- [ ] 5.4 Add selected-claim and supporting / counter-evidence interactions across workflow screens.

## 6. Quality verification

- [ ] 6.1 Add route and component tests for loading, error, empty, streaming, keyboard, and evidence status states.
- [ ] 6.2 Run lint, typecheck, tests, production build, and a local browser smoke check across all prototype routes.
- [ ] 6.3 Review the final diff for token consistency, accessible focus states, mock-data labelling, responsive layout, and forbidden backend coupling.
