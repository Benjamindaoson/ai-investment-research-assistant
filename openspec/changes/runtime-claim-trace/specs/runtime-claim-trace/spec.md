## ADDED Requirements

### Requirement: Run review exposes evidence-linked claims

The runtime workspace MUST display each claim returned by the backend as a
read-only record with its qualification status and evidence IDs.

#### Scenario: Display a detailed claim

- **WHEN** a run response contains a claim statement, task ID, status, confidence,
  and evidence IDs
- **THEN** the workspace displays the statement, task ID, status, and linked
  evidence IDs
- **AND** it displays confidence as a claim-level signal, not investment advice

#### Scenario: Display unresolved claim evidence

- **WHEN** a claim contains unresolved evidence IDs
- **THEN** the workspace marks those IDs as unresolved
- **AND** it does not present the claim as fully traceable

#### Scenario: Historical minimal claim

- **WHEN** a compatible run response contains only claim ID, status, and evidence
  IDs
- **THEN** the workspace continues to render the run
- **AND** it labels omitted claim details as unavailable rather than fabricating
  them

#### Scenario: Empty claims

- **WHEN** a run response contains no claims
- **THEN** the workspace displays an explicit empty-state message
