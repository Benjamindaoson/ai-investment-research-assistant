# Design

Synthesis remains inside the runtime because it operates on the durable
`ResearchRun` state after provider qualification. For each task, the runtime
counts evidence by stance and qualification, links only qualified records to a
claim, and sets confidence to the observed qualified/observed ratio. A task
with no qualified evidence gets a zero-confidence `NEEDS_REVIEW` claim.

The thesis contains conditional Bull/Base/Bear scenario text made only from
task titles, evidence counts, and unresolved requirement state. Its review
status is `PENDING_REVIEW` only when every task satisfies every evidence
requirement; otherwise it is `NEEDS_REVIEW`.

This is intentionally deterministic. The ceiling is that it summarizes evidence
rather than interpreting financial meaning; an analyst or a future structured
synthesis provider can add interpretation behind the same review boundary.
