## Context

`score_run` already checks memo artifacts and IC review links. Red-team
reviews are another durable, evidence-bearing artifact on `ResearchRun`, with
runtime validation that is valuable to repeat in the evaluation boundary for
legacy or mutated state.

## Goals / Non-Goals

**Goals:**

- Check Red-team review run and thesis ownership.
- Check every cited evidence ID exists in the run and has a disconfirming
  stance.
- Support optional `minimum_red_team_reviews` coverage in golden cases.

**Non-Goals:**

- No model judgment about whether a challenge is persuasive.
- No automatic reopening or state mutation during scoring.
- No universal requirement that every lightweight run has a Red-team review.

## Decisions

1. Always add a `red_team_links` check for completed or partial runs. A review
   is valid only when it belongs to the run/current thesis and all cited
   evidence is COUNTER or CONFLICTING.
2. Add `red_team_coverage` only when the case contains
   `minimum_red_team_reviews`; default cases remain compatible with runs that
   have no review.
3. Use sorted invalid IDs and an observed count in check details so failures
   are stable and do not leak reviewer prose into evaluation artifacts.

## Risks / Trade-offs

- [Existing runs have no reviews] → The default minimum is zero and the link
  check passes for an empty review list.
- [A challenge can be syntactically valid but weak] → This deterministic gate
  checks traceability only; reviewer judgment remains human-owned.
