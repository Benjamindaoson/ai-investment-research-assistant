## ADDED Requirements

### Requirement: Analyst can submit explicit linked financial inputs

The workspace MUST allow an analyst to submit period and revenue values with
qualified evidence selected from the current ResearchRun.

#### Scenario: Submit revenue analysis

- **WHEN** the analyst enters a valid period and revenue and selects qualified
  revenue evidence
- **THEN** the workspace posts the run-scoped financial analysis
- **AND** the returned durable artifact is shown in the run workspace

#### Scenario: Submit prior revenue analysis

- **WHEN** the analyst enters prior revenue
- **THEN** the workspace requires a separate prior-revenue evidence selection
- **AND** the returned growth metric remains linked to both field mappings

### Requirement: The form prevents unsupported submissions

The workspace MUST prevent submission when required values or qualified
evidence selections are missing and MUST show runtime failures without
fabricating a result.

#### Scenario: Missing required input

- **WHEN** period, revenue, or required evidence is absent
- **THEN** the submit control is disabled
- **AND** no runtime request is sent

#### Scenario: Runtime rejects the request

- **WHEN** the backend rejects the evidence-linked analysis
- **THEN** the workspace shows the error in an alert
- **AND** the prior run projection remains visible
