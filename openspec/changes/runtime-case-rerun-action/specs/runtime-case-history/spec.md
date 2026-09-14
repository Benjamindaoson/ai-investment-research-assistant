## MODIFIED Requirements

### Requirement: Analysts can inspect case-scoped run history

The live runtime workspace SHALL retrieve and display the durable runs that
belong to the current ResearchCase, including each run identifier and state,
and SHALL expose an explicit action to create the next run for that case.

#### Scenario: History is available

- **WHEN** the case history endpoint returns one or more runs
- **THEN** the workspace displays each run and marks the currently open run as
  active

#### Scenario: History is empty

- **WHEN** the case history endpoint returns an empty list
- **THEN** the workspace shows an explicit empty state without inventing runs

#### Scenario: History retrieval fails

- **WHEN** the case history endpoint returns an error
- **THEN** the current run remains visible and the history surface shows the
  error

### Requirement: Analysts can navigate to a historical run

Each displayed historical run SHALL provide a direct link to its durable run
workspace without mutating the run.

#### Scenario: Analyst opens another run

- **WHEN** the analyst activates a historical run link
- **THEN** the browser navigates to `/runtime/{run_id}` for that run
