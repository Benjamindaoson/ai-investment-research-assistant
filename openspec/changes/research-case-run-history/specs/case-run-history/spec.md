## ADDED Requirements

### Requirement: Case history returns persisted runs

The API SHALL return all persisted `ResearchRun` records linked to a case at
`GET /api/v1/research-cases/{case_id}/runs`, ordered from oldest to newest. The
response MUST preserve each run's own ID and state.

#### Scenario: Case has a rerun history

- **WHEN** a case has an initial run and one rerun
- **THEN** the endpoint returns both runs in creation order with different IDs

#### Scenario: Unknown case history

- **WHEN** a client requests history for an unknown case
- **THEN** the endpoint returns HTTP 404 rather than an empty successful list
