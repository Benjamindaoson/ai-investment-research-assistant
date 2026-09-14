## Context

FinEvidence v1 is the evidence authority. Its table evidence may contain
human-readable `value` text, but that field is not a typed numeric financial
fact contract. The investment runtime must therefore keep extraction and
calculation separate and auditable.

## Decision

Introduce `FinancialFact` and `FinancialFactSet` in the runtime domain. A fact
must carry:

- one supported `FinancialSnapshot` field;
- a decimal value supplied by an explicit extraction or analyst handoff;
- period, unit, currency, and basis (`REPORTED`, `DERIVED`, `ESTIMATE`, or
  `GUIDANCE`);
- one or more evidence IDs.

`financial_snapshot_from_facts` performs only structural mapping. It does not
parse excerpts or table text. It requires exactly one fact per snapshot field,
one common period, and a revenue fact. The API then calls the existing
`FinancialAnalysisTool` and `ResearchEngine.record_financial_analysis`, which
remain responsible for deterministic calculations and qualified-evidence
enforcement.

The analysis result stores the typed facts so a reviewer can inspect the
inputs, their basis, and their evidence links after reconstruction.

## Non-goals

- No automatic extraction from arbitrary text.
- No changes to FinEvidence or its v1 API.
- No new market-data provider.
- No LLM call or model-generated numeric fact without a typed validation
  boundary.
- No frontend workflow until the backend contract has proven stable.
