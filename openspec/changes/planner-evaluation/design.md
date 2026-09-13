## Context

The Research Runtime can now produce a validated `ResearchPlan`, but execution tests alone cannot tell whether the plan was the right plan. Planning quality must be measured before evidence collection, using an independently authored golden case rather than assertions derived from the planner implementation.

## Goals / Non-Goals

**Goals:**

- Score task coverage, expected dependency edges, evidence requirements, counter-evidence coverage, and duplicate task risk.
- Keep scores based on observed plan structure, not model self-report.
- Make the deterministic planner a reproducible baseline for future LLM planner comparisons.
- Preserve `N/A` for evaluation dimensions that require unavailable external data.

**Non-Goals:**

- Evaluating the truth of financial claims or market predictions.
- Calling an LLM or external provider.
- Building a statistical benchmark platform or a planner optimizer.

## Decisions

1. **Use authored golden cases.** Each case states the minimum required task IDs, expected dependency map, required evidence-bearing tasks, required counter-evidence tasks, and an allowed task ceiling. This keeps the reference independent from planner code.

2. **Return the existing `EvaluationResult`.** Planner checks use the same explicit PASS/FAIL/N/A/BLOCKED contract as run checks, so CI and future dashboards do not need a second result format.

3. **Separate plan and run evaluation.** The CLI prints `plan_evaluation` and `run_evaluation` separately. A plan can be structurally good while its evidence run is partial, and those facts must not collapse into one score.

4. **Treat missing requirements as failure, not a lower score.** A research plan either meets the minimum contract for a golden case or fails that check; weighted aggregate scoring can be added later when enough cases exist.

## Risks / Trade-offs

- [Golden cases encode one research style] → Keep cases small, explicit, and versioned; add diverse cases before comparing planners.
- [Structural checks do not prove financial correctness] → State this boundary in output and documentation.
- [A task can satisfy a keyword without useful content] → Require non-empty purpose, tool, and evidence requirements through domain validation.

## Migration Plan

1. Add the golden plan case and public scorer.
2. Add tests using a known deterministic plan and an independently malformed plan.
3. Extend the evaluation CLI output.
4. Run all backend/frontend checks and commit the evaluation baseline.

## Open Questions

- Human review criteria for “sufficiently specific” task purpose should be added after real analyst examples are available.
