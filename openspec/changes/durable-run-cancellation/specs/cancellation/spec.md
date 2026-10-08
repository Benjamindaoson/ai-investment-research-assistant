## ADDED Requirements

### Requirement: Run cancellation is durable and terminal

The runtime SHALL expose an explicit cancellation write path that persists a
terminal `CANCELLED` run with a completion timestamp and audit event.

#### Scenario: Cancel a created run

- **WHEN** an analyst cancels a created run
- **THEN** the run reads back as `CANCELLED`, has no synthesized thesis, and
  contains a `RUN_CANCELLED` event

#### Scenario: Cancel is repeated

- **WHEN** cancellation is requested for an already cancelled run
- **THEN** the existing run is returned without duplicate cancellation events

### Requirement: Cancelled runs cannot resume accidentally

The runtime SHALL not execute provider tasks or transition a cancelled run to a
completed state.

#### Scenario: Execute after cancellation

- **WHEN** execute is called for a cancelled run
- **THEN** the run remains cancelled and provider call count is unchanged
