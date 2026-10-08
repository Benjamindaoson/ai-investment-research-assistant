## ADDED Requirements

### Requirement: Case read returns a case contract

`GET /api/v1/research-cases/{case_id}` SHALL return the persisted
`ResearchCase`, including its ID, question, target, and creation timestamp. It
MUST NOT return a `ResearchRun` payload.

#### Scenario: Existing case

- **WHEN** a client requests an existing case ID
- **THEN** the response is HTTP 200 and contains the case fields with no run
  state substituted for them

#### Scenario: Missing case

- **WHEN** a client requests an unknown case ID
- **THEN** the response is HTTP 404 with a stable not-found detail
