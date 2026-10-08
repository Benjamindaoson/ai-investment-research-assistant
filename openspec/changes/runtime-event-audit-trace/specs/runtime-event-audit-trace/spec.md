## ADDED Requirements

### Requirement: Reviewers can inspect durable run events

The runtime workspace SHALL expose the append-only events returned by the run events endpoint as a read-only chronological audit trace.

#### Scenario: Events exist

- **WHEN** the events endpoint returns valid events for a run
- **THEN** the workspace displays each event's type, timestamp, and structured payload without changing the run

#### Scenario: No events exist

- **WHEN** the events endpoint returns an empty list
- **THEN** the workspace displays an explicit empty audit-trace state

### Requirement: Event transport is validated

The frontend service SHALL validate event identity and preserve arbitrary event payload JSON at the HTTP boundary.

#### Scenario: Valid event response

- **WHEN** the endpoint returns a run ID and event records with JSON payloads
- **THEN** the repository returns the typed event list to the query layer

#### Scenario: Invalid event response

- **WHEN** the endpoint returns an event with an invalid identity or payload shape
- **THEN** the service rejects the response and the workspace shows an explicit error state

### Requirement: Active runs refresh their event trace

The event query SHALL refresh while the associated run is non-terminal and SHALL stop polling when the run reaches a terminal state.

#### Scenario: Active run

- **WHEN** the associated run is CREATED, RUNNING, or VERIFYING
- **THEN** the event query uses the bounded runtime refresh interval

#### Scenario: Terminal run

- **WHEN** the associated run is COMPLETED, PARTIAL, FAILED, CANCELLED, or BLOCKED
- **THEN** the event query does not continue polling
