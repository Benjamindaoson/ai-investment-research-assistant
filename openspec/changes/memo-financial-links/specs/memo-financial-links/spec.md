## ADDED Requirements

### Requirement: Memos preserve financial artifact references

The runtime SHALL expose the current run-scoped FinancialAnalysis input hash
and ValuationScenarios artifact ID on the InvestmentMemo when those artifacts
are recorded, without copying or inventing calculation values.

#### Scenario: Financial artifacts are linked after recording

- **WHEN** a validated financial analysis or valuation artifact is recorded
  for a run with a memo
- **THEN** the memo contains the corresponding stable reference and the value
  survives persistence read-back

#### Scenario: Historical memo remains compatible

- **WHEN** a stored memo has no financial artifact reference fields
- **THEN** it loads with null references and no synthetic artifact is created

### Requirement: Analysts can inspect financial memo references

The typed workspace and Markdown export SHALL expose memo financial artifact
references when present and SHALL preserve an explicit absent state when no
artifact exists.

#### Scenario: Export contains financial provenance

- **WHEN** a memo contains financial artifact references
- **THEN** the workspace summary and Markdown export show those references
