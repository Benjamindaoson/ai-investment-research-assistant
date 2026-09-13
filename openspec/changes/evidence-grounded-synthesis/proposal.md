# Evidence-grounded synthesis

## Why

The runtime currently creates claims and a thesis with fixed investment language
that is not derived from the evidence records collected for a run. That makes a
completed run look more authoritative than its observed evidence warrants.

## What changes

- Replace fixed synthesis text with deterministic summaries of qualified,
  counter, conflicting, and unresolved evidence.
- Link each claim only to evidence records from its task and derive confidence
  from observed qualification rather than a hardcoded value.
- Keep thesis scenarios conditional and review-gated; do not invent financial
  facts or investment conclusions.

## Out of scope

- LLM-generated investment prose.
- Financial data ingestion or a second retrieval system.
- Changes to the FinEvidence provider boundary.
