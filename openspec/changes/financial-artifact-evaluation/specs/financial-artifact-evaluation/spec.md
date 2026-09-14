## ADDED Requirements

### Requirement: Financial artifacts are evaluated for evidence integrity

The deterministic run evaluator SHALL verify every evidence ID present in a
FinancialAnalysis or ValuationScenarios artifact resolves to a QUALIFIED
evidence record in the evaluated run. Missing or unqualified IDs MUST fail the
corresponding named link check.

#### Scenario: Evidence-linked financial artifacts pass

- **WHEN** present financial artifacts reference only current-run qualified
  evidence
- **THEN** the evaluator records passing financial artifact link checks

#### Scenario: Invalid financial artifact evidence fails

- **WHEN** a financial artifact references missing or unqualified evidence
- **THEN** the evaluator records the corresponding link check as FAIL with
  sorted IDs

### Requirement: Golden cases may require financial artifacts

The evaluator SHALL support `requires_financial_analysis` and
`requires_valuation_scenarios` golden-case fields. When either is true, the
corresponding artifact MUST be present; absent requirements MUST NOT create a
presence failure.

#### Scenario: Required financial artifact is absent

- **WHEN** a golden case requires an artifact that is not present on the run
- **THEN** the corresponding presence check FAILS and the result does not pass

#### Scenario: Optional financial artifacts remain compatible

- **WHEN** a golden case does not require financial artifacts
- **THEN** no artifact-presence failure is added for absent artifacts
