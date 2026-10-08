## Context

`InvestmentMemo` now contains five stable sections and flat claim/evidence/
unresolved ID lists. `score_run` is the existing deterministic evaluation
boundary and already receives the complete `ResearchRun`.

## Goals / Non-Goals

**Goals:**

- Detect missing or duplicate required sections.
- Detect section links that reference artifacts outside the run.
- Keep evaluation deterministic and explain failures by check name.

**Non-Goals:**

- Judging writing quality, investment correctness, or model confidence.
- External benchmark data or LLM-as-judge scoring.

## Decisions

Add two checks to every local run evaluation: `memo_sections` verifies the exact
five section keys and non-empty bodies; `memo_artifact_links` verifies claim,
evidence, and unresolved IDs are subsets of the run's corresponding artifacts.
The checks fail when no memo exists, because the evaluated run contract is a
reviewable memo-producing runtime.

## Risks / Trade-offs

- [Risk] Historical runs without structured sections fail the newer evaluator →
  Mitigation: the domain field remains backward-compatible, while evaluation
  accurately reports that those runs do not meet the current contract.

## Migration Plan

No data migration. Re-run or regenerate old runs before using the new score as a
release gate.
