## ADDED Requirements

### Requirement: PostgreSQL durable runtime store

The runtime SHALL use PostgreSQL for cases, runs, append-only events, checkpoints, leases, evaluations, and investment memory when a PostgreSQL URL is configured.

#### Scenario: Persist and reload a PostgreSQL run

- **WHEN** the API creates a case and run with PostgreSQL configured
- **THEN** a separately started worker or API process can reload the same run, events, checkpoint, evaluation, and memory payloads from PostgreSQL

#### Scenario: Preserve lease ownership semantics

- **WHEN** two local runtime processes attempt to acquire the same run lease
- **THEN** exactly one lease acquisition succeeds and the other execution is rejected without overwriting the owner's state

### Requirement: Redis durable dispatch

The runtime SHALL publish a run ID to Redis after persisting its `RUN_ENQUEUED` event, and the worker SHALL be able to consume that run ID and execute the run.

#### Scenario: Enqueue and consume a run

- **WHEN** a client calls the enqueue endpoint with Redis configured
- **THEN** the API returns the queued state, Redis contains a dispatch item, and a worker process executes the corresponding PostgreSQL-backed run

#### Scenario: Recover after Redis dispatch loss

- **WHEN** a `RUN_ENQUEUED` event exists in PostgreSQL but the Redis item is missing
- **THEN** the worker's database scan fallback still discovers and executes the runnable run

### Requirement: Local Compose startup

The repository SHALL provide a single-machine Docker Compose configuration that starts PostgreSQL, Redis, and the runtime with health checks and documented environment variables.

#### Scenario: Start the local stack

- **WHEN** the user runs `docker compose up --build`
- **THEN** PostgreSQL and Redis become healthy and the runtime health endpoint reports the configured persistence and queue modes

#### Scenario: Use FinEvidence without coupling repositories

- **WHEN** `FIN_EVIDENCE_BASE_URL` points to the separately running FinEvidence API
- **THEN** the composed runtime uses the existing HTTP boundary and does not import FinEvidence implementation modules

### Requirement: SQLite compatibility

The runtime SHALL retain SQLite fallback and explicit store injection for tests when no PostgreSQL URL is configured.

#### Scenario: Run the test suite without services

- **WHEN** PostgreSQL and Redis environment variables are absent
- **THEN** the existing SQLite-backed unit and API tests run without network services
