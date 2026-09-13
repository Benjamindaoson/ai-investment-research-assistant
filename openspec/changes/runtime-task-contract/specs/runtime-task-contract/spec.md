## ADDED Requirements

### Requirement: Run review exposes the task contract

The runtime workspace MUST display each returned task's state and, when
available, its purpose, dependencies, and evidence requirements.

#### Scenario: Display a detailed task contract

- **WHEN** a run response contains detailed task fields
- **THEN** the workspace displays task purpose, dependency IDs, and each
  evidence requirement's description, minimum records, and required stances

#### Scenario: Display missing requirements

- **WHEN** a task contains missing requirement IDs
- **THEN** the workspace displays those IDs as unresolved
- **AND** it does not claim the task contract is fully satisfied

#### Scenario: Historical minimal task

- **WHEN** a compatible response contains only task ID, title, and state
- **THEN** the workspace continues to render the task
- **AND** it labels omitted contract details as unavailable
