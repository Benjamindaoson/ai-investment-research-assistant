## Context

`ResearchRun` already stores RedTeamReview objects and `InvestmentMemo` stores
counter-evidence IDs. IC reviews recently gained an analogous memo link. The
same explicit relationship is needed for disconfirming review provenance.

## Goals / Non-Goals

**Goals:**

- Preserve review IDs in the memo as an append-only projection.
- Keep old stored memos readable with an empty default.
- Show the IDs in the workspace and Markdown export.

**Non-Goals:**

- No copy of reviewer prose into the memo.
- No automatic decision or thesis status changes beyond existing Red-team
  behavior.
- No new endpoint or persistence table.

## Decisions

1. Add a bounded `red_team_review_ids` list to `InvestmentMemo`, defaulting to
   an empty list for historical payloads.
2. The existing `record_red_team_review` write authority appends the accepted
   review ID after runtime validation, preserving the same ordering as the
   run's review list.
3. Frontend schemas use the same default and render only the count/IDs; the
   full review remains available on the run projection.

## Risks / Trade-offs

- [A legacy memo may contain a review ID not present on the run] → Preserve it
  for audit read-back; deterministic evaluation reports the broken relation.
- [The list can grow with repeated review cycles] → Keep the existing bounded
  list convention and no unbounded prose duplication.
