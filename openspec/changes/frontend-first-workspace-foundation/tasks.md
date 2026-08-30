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
- [ ] 3.4 Expand runtime schemas, service interfaces, repositories, and query/mutation hooks to cover every P0 read and domain operation without UI fixture imports.

## 4. Today and New Research

- [x] 4.1 Implement the Today research worklist and operational context pane using the first supplied reference's layout and density.
- [x] 4.2 Implement the New Research input workflow with validation, attachment mock state, and handoff to a Research Case.
- [ ] 4.3 Add responsive and interaction tests for the Today navigation and New Research submission.

## 5. Batch 2 — Research execution

- [x] 5.1 Implement Research Case overview with research question/goal, editable prioritized plan tasks, evidence coverage, and explicit mock status.
- [x] 5.2 Implement cancellable/restartable streaming research with named activity stages and progressively revealed structured Findings.
- [x] 5.3 Implement Finding expansion with confidence status, supporting signals, evidence counts, and counter-evidence counts.
- [x] 5.4 Add execution, plan-control, cancellation, restart, and progressive-finding tests.

## 6. Batch 3 — Evidence intelligence

- [x] 6.1 Implement the three-column Evidence Workspace with claim selection and separate supporting, counter, conflicting, and unverified evidence treatment.
- [x] 6.2 Expose complete source intelligence and citation context through the query/repository boundary.
- [x] 6.3 Implement evidence-status changes, claim approve/reject actions, and request-more-research interactions with audit records.
- [x] 6.4 Add evidence semantics, provenance, selection, mutation, and responsive workspace tests.

## 7. Batch 4 — Decision workspaces

- [x] 7.1 Implement Company Research with current thesis, What Changed, technology, commercialization, competition, talent, funding, risks, and coverage.
- [x] 7.2 Implement structured Thesis Workspace with key assumptions, linked supporting/counter evidence, and disconfirming conditions.
- [x] 7.3 Implement Risk / Catalyst and What to Monitor workspaces with analyst-editable mock items.
- [x] 7.4 Add company/thesis/risk/catalyst/monitor interaction and semantic-state tests.

## 8. Batch 5 — Review, outputs, and library

- [ ] 8.1 Implement Human Review queue and audit trail for claim, finding, evidence, thesis, note, more-research, and brief actions.
- [ ] 8.2 Implement all Product Spec Living Brief sections with analyst notes and mock approval.
- [ ] 8.3 Implement version history, What Changed, and structured version diff.
- [ ] 8.4 Implement the basic Research Library with search, tag, company, industry, and source-type filters.
- [ ] 8.5 Add review, approval, version diff, and library filter tests.

## 9. End-to-end quality verification

- [ ] 9.1 Complete route/navigation coverage and tests for loading, error, empty, streaming, keyboard, review, and evidence states.
- [ ] 9.2 Run lint, strict typecheck, tests, production build, and a local browser smoke check across the full P0 path.
- [ ] 9.3 Review the final diff for Product Spec coverage, evidence semantics, token consistency, accessible focus states, mock-data labelling, responsive layout, and forbidden backend/runtime coupling.
