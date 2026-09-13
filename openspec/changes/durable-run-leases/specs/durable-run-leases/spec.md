## ADDED Requirements

### Requirement: Research run execution has persistent exclusive ownership
The runtime SHALL acquire an expiring persistent lease before executing any non-terminal research run. At most one unexpired lease MUST exist for a run, and lease release MUST require the current lease token.

#### Scenario: First executor acquires a lease
- **WHEN** an executor starts a non-terminal run with no active lease
- **THEN** the store records one lease token and expiry, and execution proceeds

#### Scenario: Concurrent executor is rejected
- **WHEN** a second executor starts the same run while the first lease is unexpired
- **THEN** the second executor receives an explicit conflict error and the evidence provider is not invoked by that attempt

#### Scenario: Expired ownership can be reclaimed
- **WHEN** the stored lease has expired after an executor crash or interruption
- **THEN** a later executor deletes the expired ownership, acquires a new token, and resumes from persisted run state or checkpoint

#### Scenario: Terminal runs do not create leases
- **WHEN** an executor is asked to execute a COMPLETED, PARTIAL, FAILED, or CANCELLED run
- **THEN** it returns the terminal run without creating a new lease or provider execution

### Requirement: Lease lifecycle is auditable
The runtime SHALL append lease acquisition and release events containing the run ID and lease token, and SHALL release the lease on success, failure, cancellation, and early checkpointed return.

#### Scenario: Successful execution records lifecycle events
- **WHEN** a run completes normally
- **THEN** its event stream contains a matching `RUN_LEASE_ACQUIRED` and `RUN_LEASE_RELEASED` pair

#### Scenario: Provider failure does not strand ownership
- **WHEN** provider execution raises an error after lease acquisition
- **THEN** the run is marked failed, the lease is released, and a later attempt is not blocked by the failed executor's token

#### Scenario: Stop-after-tasks releases ownership
- **WHEN** execution returns after the requested number of tasks for checkpointed resume
- **THEN** the run retains its checkpoint and the lease is released before the response returns

### Requirement: Lease conflict is explicit at the HTTP boundary
The API SHALL map an active lease conflict to HTTP 409 with a stable error detail and SHALL NOT silently retry or fall back to another provider.

#### Scenario: API reports active execution conflict
- **WHEN** `POST /api/v1/research-runs/{run_id}/execute` targets a run with an active lease
- **THEN** the API responds with HTTP 409 and a conflict detail
