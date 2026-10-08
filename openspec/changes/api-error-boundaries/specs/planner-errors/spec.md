## ADDED Requirements

### Requirement: Case creation exposes planner failure semantics

The API SHALL translate planner provider failures to HTTP 503 and plan contract
or validation failures to HTTP 422 without silently falling back.

#### Scenario: Planner provider unavailable

- **WHEN** the selected planner raises `PlannerProviderError` while creating a
  case
- **THEN** the API returns 503 with an actionable error detail and no case/run
  is persisted

#### Scenario: Plan contract rejected

- **WHEN** the planner returns a plan that fails canonical validation
- **THEN** the API returns 422 and no case/run is persisted

### Requirement: API errors preserve durable truth

The API SHALL not report a created case when planner execution has failed.

#### Scenario: Failed creation is read back

- **WHEN** a case creation request receives a planner error
- **THEN** the associated case and run cannot be read from the store
