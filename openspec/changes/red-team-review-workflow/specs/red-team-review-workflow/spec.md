## ADDED Requirements

### Requirement: Analyst can record a disconfirming review

The runtime workspace MUST allow an analyst to submit reviewer, challenge,
rationale, outcome, and one or more counter or conflicting evidence records for
the current synthesized thesis.

#### Scenario: Submit a red-team review

- **WHEN** the run has a synthesized thesis and disconfirming evidence and the analyst submits valid review fields
- **THEN** the workspace posts the run-scoped red-team review
- **AND** the returned durable run projection is rendered

#### Scenario: Evidence options are constrained

- **WHEN** the review form renders
- **THEN** it offers only current-run evidence whose stance is COUNTER or CONFLICTING
- **AND** it does not offer supporting evidence or evidence from another run

### Requirement: Review submission remains auditable

The workspace MUST preserve the backend response and show the saved review
outcome and rationale without fabricating a successful review on failure.

#### Scenario: Review is rejected

- **WHEN** the backend rejects the review request
- **THEN** the workspace shows the failure in an alert
- **AND** the current run projection remains visible
- **AND** no success message is shown

#### Scenario: Review is saved

- **WHEN** the backend accepts the review request
- **THEN** the workspace updates the cached run with the returned review
- **AND** the workspace shows a saved status message
