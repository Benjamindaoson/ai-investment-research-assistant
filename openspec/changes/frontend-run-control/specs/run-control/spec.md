## ADDED Requirements

### Requirement: Connected frontend can durably cancel a run

The frontend SHALL expose `cancelRun` through its typed runtime service and
repository, posting the analyst reason to the canonical backend endpoint.

#### Scenario: Cancellation succeeds

- **WHEN** the backend returns a cancelled run
- **THEN** the repository returns its validated identifier and `CANCELLED` state

#### Scenario: Cancellation fails

- **WHEN** the backend returns an HTTP error or invalid payload
- **THEN** the repository rejects the operation without fabricating a terminal
  state
