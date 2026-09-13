# Thesis delta

## Why

Investment Memory currently retains version IDs but cannot show how a new run
changed the observed research state. A memory system needs a reviewable delta
without inventing confidence or financial conclusions.

## What changes

- Add a typed `ThesisDelta` containing prior/current thesis references and
  observed evidence/unresolved requirement count deltas.
- Compute it when a subsequent run for the same target creates a memo.
- Persist and expose the latest delta through Investment Memory.

## Out of scope

- Semantic LLM comparison, confidence prediction, or automatic thesis rewrite.
- Claiming that evidence-count deltas imply investment performance.
