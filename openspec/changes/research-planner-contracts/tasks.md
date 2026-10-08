## 1. Planning domain

- [x] 1.1 Add `ResearchPlan` and planner metadata to the domain contracts.
- [x] 1.2 Add the `ResearchPlanner` protocol and deterministic financial planner.
- [x] 1.3 Add planner and invalid-output contract tests.

## 2. Runtime integration

- [x] 2.1 Make run creation validate planner output before persistence and record plan provenance.
- [x] 2.2 Preserve plan/task separation through execution, checkpoint, and resume.
- [x] 2.3 Add plan persistence and API read tests.

## 3. Product boundary and verification

- [x] 3.1 Add `GET /api/v1/research-runs/{run_id}/plan` and stable 404 behavior.
- [x] 3.2 Document deterministic planning versus future LLM planning.
- [x] 3.3 Run backend checks, frontend checks, evaluation, API smoke, OpenSpec validation, and final Git audit.
