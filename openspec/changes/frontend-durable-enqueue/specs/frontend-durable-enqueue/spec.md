## ADDED Requirements

### Requirement: Live runtime can enqueue durable research work

The live runtime workspace MUST expose the existing durable enqueue operation
through its typed service and repository boundaries.

#### Scenario: Queue a created run

- **WHEN** an analyst submits a CREATED run to the durable queue
- **THEN** the frontend sends `POST /api/v1/research-runs/{run_id}/enqueue`
- **AND** the returned run control state is reflected in the runtime query
- **AND** pending and request error states remain visible to the analyst.

#### Scenario: Queue a partial run for recovery

- **WHEN** an analyst submits a PARTIAL run to the durable queue
- **THEN** the same typed enqueue operation is available
- **AND** the frontend refreshes the run and case history after success.

### Requirement: Synchronous local execution remains available

The enqueue integration MUST NOT remove the existing direct execute action for
interactive local runs.

#### Scenario: Start a created run locally

- **WHEN** a CREATED run is shown in the live workspace
- **THEN** the analyst can still invoke the direct Start research action.
