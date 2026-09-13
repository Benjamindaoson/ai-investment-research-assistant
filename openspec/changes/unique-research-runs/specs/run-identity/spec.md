## ADDED Requirements

### Requirement: Each research run has an independent identity

The runtime SHALL assign a unique opaque ID to every newly created
`ResearchRun`. Multiple runs for the same `ResearchCase` MUST remain separately
persisted with the same `case_id` relationship.

#### Scenario: Two runs for one case

- **WHEN** the runtime creates two runs for the same case
- **THEN** their IDs differ and reading either ID returns its own run state,
  plan, events, and checkpoints

#### Scenario: API returns the created run identity

- **WHEN** a client creates a research case through the API
- **THEN** the response contains the opaque run ID that can be used with all run
  endpoints
