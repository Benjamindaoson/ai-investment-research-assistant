## ADDED Requirements

### Requirement: Financial analysis is durable within a research run

The runtime MUST persist the latest evidence-linked financial analysis on the
ResearchRun after a successful calculation, including its exact field-level
evidence mapping.

#### Scenario: Analysis survives a run read

- **WHEN** a valid analysis is posted for a run
- **THEN** the response contains the calculation and evidence mapping
- **AND** a subsequent run read contains the same financial_analysis artifact

#### Scenario: Analysis survives runtime reconstruction

- **WHEN** a valid analysis is posted and the runtime is reconstructed from
  the same SQLite store
- **THEN** the run read still contains the financial_analysis artifact

### Requirement: Financial analysis writes are auditable

The runtime MUST append a FINANCIAL_ANALYSIS_RECORDED event after persisting a
successful analysis.

#### Scenario: Analysis event records the artifact

- **WHEN** a valid run-scoped analysis is written
- **THEN** the run events include FINANCIAL_ANALYSIS_RECORDED
- **AND** the event identifies the analysis period and linked evidence fields

### Requirement: Persisted analysis is readable through a typed boundary

The runtime MUST expose the persisted artifact through a GET endpoint and the
frontend MUST parse it through the existing typed service/repository boundary.

#### Scenario: Read an existing artifact

- **WHEN** the client requests financial analysis for a run with an artifact
- **THEN** the API returns the persisted calculation
- **AND** an unknown run returns 404
