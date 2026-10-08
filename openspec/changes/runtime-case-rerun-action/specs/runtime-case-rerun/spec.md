## ADDED Requirements

### Requirement: Analysts can create a new run for an existing case

The runtime workspace SHALL allow an analyst to explicitly create a new durable
ResearchRun for the current ResearchCase without changing the existing run.

#### Scenario: Rerun creation succeeds

- **WHEN** the analyst activates the new run action and the runtime accepts the
  case
- **THEN** the client navigates to the returned run workspace and case history
  is invalidated for a later read

#### Scenario: Rerun creation fails

- **WHEN** the runtime rejects the new run request
- **THEN** the current run remains visible and the backend error is shown

#### Scenario: Rerun is pending

- **WHEN** the create request is in flight
- **THEN** the action is disabled and cannot issue a duplicate request

### Requirement: Rerun creation remains explicit

The client SHALL create a new run only after an analyst activates the action;
it SHALL NOT automatically execute the run or alter the previous run.

#### Scenario: New run is created but not executed

- **WHEN** creation returns successfully
- **THEN** the client navigates to the new run without issuing an execute
  request
