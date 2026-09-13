## ADDED Requirements

### Requirement: Active run leases are renewable
The runtime SHALL renew an active run lease periodically while execution is in progress, and renewal MUST require the current `(run_id, lease_id)` pair.

#### Scenario: Slow provider remains owned
- **WHEN** a provider call runs longer than one heartbeat interval but the store remains available
- **THEN** the current executor renews the lease before expiry and remains the only valid writer

#### Scenario: Wrong owner cannot renew
- **WHEN** a renewal request uses a stale or different lease token
- **THEN** the store rejects the renewal and does not extend the active owner's expiry

### Requirement: Stale executors cannot persist state
Run payload, checkpoint, and event writes performed during execution SHALL be conditional on an unexpired current lease. If ownership is lost, the executor MUST raise an explicit lease-loss error before accepting provider results or writing further execution state.

#### Scenario: Ownership loss discards provider result
- **WHEN** lease renewal fails while a provider call is in flight
- **THEN** the executor does not persist that call's result as a successful task and surfaces lease loss explicitly

#### Scenario: Current owner can persist normally
- **WHEN** the lease token is current and unexpired
- **THEN** guarded run, checkpoint, and event writes succeed

### Requirement: Takeover recovers abandoned task state
When a new executor acquires an expired lease, the runtime SHALL reset persisted `RUNNING` tasks to `PENDING` before continuing and SHALL record the recovery in the run event stream.

#### Scenario: Crashed task is recoverable
- **WHEN** a prior executor left a task in `RUNNING` and its lease expired
- **THEN** the new executor records `TASK_RECOVERED`, resets the task to `PENDING`, and can resume the DAG

### Requirement: Lease-loss outcomes remain auditable
The runtime SHALL record lease release with whether the token was released and whether heartbeat loss was observed, without converting lease loss into a successful run.

#### Scenario: Heartbeat loss is visible
- **WHEN** an executor loses lease ownership
- **THEN** its lifecycle event includes `heartbeat_lost=true` and the run is not reported as successfully completed by that executor
