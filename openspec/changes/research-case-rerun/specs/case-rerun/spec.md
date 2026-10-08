## ADDED Requirements

### Requirement: Existing cases can create independent runs

The API SHALL create a new `ResearchRun` from the persisted `ResearchCase` at
`POST /api/v1/research-cases/{case_id}/runs`. The request MUST NOT accept or
override case target or question data.

#### Scenario: Rerun existing case

- **WHEN** a client posts to the run creation endpoint for an existing case
- **THEN** the API returns HTTP 201 with a new opaque run ID linked to that case

#### Scenario: Unknown case

- **WHEN** a client posts to the endpoint for an unknown case
- **THEN** the API returns HTTP 404 and persists no run

#### Scenario: Rerun preserves original history

- **WHEN** a case is rerun after an earlier run exists
- **THEN** both run IDs remain readable and the earlier run payload is unchanged
