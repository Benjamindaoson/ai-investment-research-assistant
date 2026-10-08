## ADDED Requirements

### Requirement: Live run pages observe non-terminal durable state

The live runtime workspace SHALL refetch the run and trace through the existing
typed service boundary at a bounded interval while the run is non-terminal.

#### Scenario: In-flight run refreshes

- **WHEN** the loaded run is in CREATED, RUNNING, or VERIFYING state
- **THEN** the run and trace queries schedule periodic refreshes at the
  configured live interval

#### Scenario: Terminal run stops refreshing

- **WHEN** the run reaches COMPLETED, PARTIAL, FAILED, CANCELLED, or BLOCKED
- **THEN** the run and trace queries stop periodic refetching

### Requirement: Runtime controls keep related views coherent

After execute, replan, or cancel mutations, the workspace SHALL immediately
project the returned run when available and refresh related case history and
trace state.

#### Scenario: Execution result updates the page

- **WHEN** an execute mutation returns a run
- **THEN** the run view displays the returned state and schedules or stops
  polling according to that state

#### Scenario: Cancellation does not leave stale trace

- **WHEN** cancellation succeeds
- **THEN** the run and trace queries are invalidated so the durable terminal
  outcome is read back
