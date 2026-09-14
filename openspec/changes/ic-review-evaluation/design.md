## Context

`score_run` already validates memo section completeness and claim/evidence/
requirement references. IC review IDs are now an additional artifact relation:
the memo can reference reviews and a decision can reference reviews. Golden
cases also need a way to demand a full or partial review panel, while ordinary
local runs must remain valid without panel input.

## Goals / Non-Goals

**Goals:**

- Validate memo and decision review IDs against the current run.
- Validate review ownership by run and thesis.
- Support optional `required_ic_review_roles` in a golden case.
- Report failures as named deterministic evaluation checks.

**Non-Goals:**

- No consensus score, reviewer weighting, recommendation generation, or model
  judgment.
- No requirement that every run collect all five roles.
- No changes to persistence or execution behavior.

## Decisions

1. **Always run link integrity; conditionally run coverage.** Every completed or
   partial run gets an `ic_review_links` check. `ic_review_coverage` is added
   only when the golden case declares `required_ic_review_roles`, preserving
   compatibility with existing cases.

2. **Validate both sides of every relation.** A review must exist in the run,
   carry the run ID, and match the current thesis when one exists. Memo and
   decision references are checked independently so a dangling relation cannot
   hide behind another valid relation.

3. **Use bounded, stable details.** Details contain sorted missing IDs and
   observed/required role names, making failures reproducible and useful in
   evaluation artifacts without including reviewer prose.

## Risks / Trade-offs

- [Old runs have no IC fields] → Pydantic defaults provide empty lists and the
  no-review path passes link integrity.
- [A golden case requires roles not appropriate to a workflow] → Keep role
  coverage opt-in per case rather than hard-coding a universal gate.
