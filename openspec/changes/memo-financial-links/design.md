## Context

`ResearchRun` stores FinancialAnalysis and ValuationScenarios artifacts after
the memo may already exist. The memo needs a small explicit reference that can
be updated by those existing write authorities without copying calculated
values into memo prose.

## Goals / Non-Goals

**Goals:**

- Bind the memo to the current financial analysis input hash and valuation
  artifact ID.
- Preserve old payload compatibility.
- Show references in the analyst UI and exported Markdown.

**Non-Goals:**

- No duplicate financial values in the memo.
- No recalculation or automatic valuation generation.
- No new API endpoints or storage tables.

## Decisions

1. Use `financial_analysis_input_hash` as the stable identity for the current
   FinancialAnalysisResult, which has no separate ID, and
   `valuation_scenarios_id` for the already identified valuation artifact.
2. Update references in `record_financial_analysis` and
   `record_valuation_scenarios`, the existing write authorities.
3. Use nullable frontend fields so historical memos remain readable and the UI
   can distinguish absent work from a fabricated reference.

## Risks / Trade-offs

- [A later artifact replaces an earlier one] → The memo points to the current
  run projection; the append-only event stream retains the recording history.
- [Old memo payloads lack fields] → Domain and Zod defaults preserve null
  compatibility.
