## ADDED Requirements

### Requirement: Complete MVP workflow

The backend SHALL expose one typed local workflow that executes a research run and records financial analysis, valuation scenarios, red-team review, five-role IC review, a human decision, and a deterministic evaluation in that order.

#### Scenario: Complete a deterministic local run

- **WHEN** a client posts valid typed facts and evidence-linked review, valuation, and decision inputs for a created or queued run
- **THEN** the backend executes the research run, persists every downstream artifact, records an evaluation, and returns a receipt with terminal state `COMPLETED`

#### Scenario: Complete an already executed run

- **WHEN** a client posts the workflow request for a completed run with no conflicting existing artifact IDs
- **THEN** the backend uses the existing run and persists the missing downstream artifacts without re-executing completed research tasks

### Requirement: Evidence and input qualification

The workflow SHALL accept only a `FinancialFactSet` with explicit evidence IDs and SHALL route it through the existing qualified-evidence validation before recording financial analysis or valuation.

#### Scenario: Reject an unqualified fact link

- **WHEN** any financial fact or valuation assumption references missing or non-`QUALIFIED` evidence in the run
- **THEN** the workflow returns a validation error and does not report a successful evaluation

#### Scenario: Reject inferred financial values

- **WHEN** the request omits the typed fact set or provides values outside its schema
- **THEN** the request is rejected before financial analysis and no excerpt parsing or implicit inference occurs

### Requirement: Explicit human review and decision

The complete workflow SHALL require one explicit review for each IC role `BULL`, `BEAR`, `FINANCIAL`, `INDUSTRY`, and `PARTNER`, plus an explicit decision rationale targeted at the current thesis.

#### Scenario: Record complete review coverage

- **WHEN** all five role inputs reference valid run evidence and contain reviewer rationales
- **THEN** the backend persists five IC review artifacts and includes all five review IDs in the workflow receipt and evaluation

#### Scenario: Reject incomplete review coverage

- **WHEN** an IC role is duplicated or omitted
- **THEN** the workflow returns a validation error before the decision is recorded

### Requirement: Durable workflow receipt

The workflow SHALL persist the normal runtime events and evaluation artifact and SHALL return identifiers sufficient to retrieve the run, memo, trace, events, financial analysis, valuation scenarios, reviews, decision, and evaluation through existing endpoints.

#### Scenario: Retrieve the completed artifact chain

- **WHEN** the workflow returns a successful receipt
- **THEN** GET requests for the run, memo, trace, financial analysis, valuation scenarios, reviews, events, and evaluation return the persisted artifacts

#### Scenario: Stop on incomplete research

- **WHEN** research execution ends in `PARTIAL`, `BLOCKED`, `FAILED`, or another non-complete state
- **THEN** the workflow stops before downstream synthesis artifacts are accepted and returns the observed state and actionable error
