## Context

`ResearchRun` already persists red-team reviews and decisions as JSON-backed
append-only artifacts. A generic red-team challenge is intentionally limited to
counter/conflicting evidence, while an IC panel needs both supporting and
disconfirming views across several roles. The existing run envelope is the
right durable boundary; adding a separate store or workflow engine would
duplicate state and create a second review authority.

## Goals / Non-Goals

**Goals:**

- Add one typed `InvestmentCommitteeReview` artifact with role and position
  enums, evidence links, reviewer, rationale, and recommendation.
- Validate thesis/run/evidence ownership before persistence.
- Expose create/list endpoints and typed frontend mutation/read-back.
- Let a decision reference review IDs when the analyst chooses to do so.

**Non-Goals:**

- No automatic scoring, consensus calculation, or recommendation generation.
- No requirement that all five roles be completed before a decision; teams may
  use a subset during screening, while the UI makes role coverage visible.
- No replacement of the existing red-team challenge workflow.
- No new database migration; the existing run JSON persistence is sufficient.

## Decisions

1. **Add a new artifact instead of overloading `RedTeamReview`.** Red-team
   evidence has a mandatory counter/conflicting stance, which is incorrect for
   Bull, Financial, or Partner reviews. A separate model keeps semantics
   explicit and avoids weakening an existing invariant.

2. **Use append-only records with repeatable roles.** More than one reviewer
   may submit the same role; the runtime preserves each record and the UI
   reports coverage by role. The record ID is the idempotency boundary.

3. **Require evidence IDs to resolve to evidence already in the run.** Both
   qualified and unresolved records may be cited because a reviewer may be
   documenting an evidence gap. The artifact never promotes evidence or
   fabricates provenance; qualification remains on each evidence record.

4. **Make decision references additive.** `DecisionRecord.review_ids` defaults
   to an empty list for backward compatibility. When supplied, every ID must
   belong to the run and current thesis, making the analyst's review basis
   auditable without silently blocking historical or lightweight decisions.

## Risks / Trade-offs

- [A panel can be incomplete] → Persist explicit role coverage and show missing
  roles; do not synthesize consensus.
- [Reviewers cite unresolved evidence] → Preserve the evidence qualification
  state and show it alongside review links; never upgrade it in review code.
- [Old SQLite payloads lack the new list] → Pydantic defaults load old runs as
  `ic_reviews=[]` and `review_ids=[]`.
