## ADDED Requirements

### Requirement: Queue intent must be durable and explicit

The runtime MUST persist a queue event for a `CREATED` or `PARTIAL` run when an
analyst calls the enqueue endpoint. Enqueue MUST NOT claim that the run has
completed.

#### Scenario: Enqueue a new run

- **WHEN** an existing `CREATED` run is enqueued
- **THEN** the API returns `202`
- **AND** the response identifies the run as queued
- **AND** a `RUN_ENQUEUED` event is persisted.

#### Scenario: Enqueue a terminal run

- **WHEN** a `COMPLETED`, `FAILED`, `CANCELLED`, or `BLOCKED` run is enqueued
- **THEN** the API returns the current terminal state without changing it
- **AND** no false completion event is written.

### Requirement: Worker execution must reuse the durable engine

The worker MUST execute only persisted `CREATED`, `RUNNING`, or `PARTIAL` runs and MUST
call the existing `ResearchEngine.execute` path so checkpoints, leases, tool
receipts, evidence qualification, and failure states remain authoritative.

#### Scenario: Worker completes a queued run

- **WHEN** the worker runs once against a database containing a runnable case
- **THEN** the run reaches the same terminal state as synchronous execution
- **AND** its memo, evidence, and event history are persisted.

#### Scenario: Unqueued run remains pending

- **WHEN** a `CREATED` run has no `RUN_ENQUEUED` event
- **THEN** a worker scan leaves it in `CREATED`
- **AND** the worker does not execute it implicitly.

#### Scenario: Worker restarts after an interrupted run

- **WHEN** a persisted run is `RUNNING` or `PARTIAL`
- **THEN** a later worker invocation considers it runnable
- **AND** execution resumes through the existing checkpoint path without
  creating duplicate successful tool results.

### Requirement: Concurrent workers fail safely

The worker MUST rely on the existing durable lease and MUST NOT overwrite a run
owned by another executor.

#### Scenario: Lease conflict

- **WHEN** another executor holds the run lease
- **THEN** the worker observes the conflict and leaves the run projection
  unchanged for the other executor to finish.

### Requirement: Operation remains locally operable

The worker MUST expose a one-shot mode and a bounded polling mode without a
new infrastructure dependency.

#### Scenario: One-shot worker

- **WHEN** an operator runs `python -m deepresearch.worker --once`
- **THEN** all currently runnable persisted runs are attempted once
- **AND** the process exits after the scan.
