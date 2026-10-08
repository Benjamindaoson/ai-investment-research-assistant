## ADDED Requirements

### Requirement: Live workspace controls a canonical runtime run

The frontend SHALL create, read, execute, and cancel runtime runs through typed
service and repository methods, and SHALL render backend state rather than
fabricating progress.

#### Scenario: Execute a created run

- **WHEN** the analyst starts a runtime run
- **THEN** the workspace displays the returned task state, evidence coverage,
  and memo status from the backend

#### Scenario: Cancel a run

- **WHEN** the analyst cancels a non-terminal runtime run
- **THEN** the workspace displays `CANCELLED` from the backend and does not
  locally mark the run completed

### Requirement: Browser transport is bounded by explicit local CORS

The backend SHALL allow configured development origins and SHALL not default to
a wildcard origin.

#### Scenario: Local frontend calls runtime

- **WHEN** a request originates from the configured local frontend origin
- **THEN** the backend returns the appropriate CORS headers
