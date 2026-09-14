## Why

The single-machine MVP currently proves the research artifact chain on SQLite, but it does not yet exercise the database and queue boundaries expected by the product's backend. Adding PostgreSQL and Redis now makes the local setup representative enough for an MVP demo while keeping deployment and operations deliberately simple.

## What Changes

- Add a PostgreSQL-backed implementation of the existing durable runtime store contract.
- Add a Redis-backed run queue while retaining the append-only database enqueue event as the durable audit record.
- Select PostgreSQL and Redis from environment variables without breaking SQLite-based tests and fallback development.
- Add Docker Compose services for PostgreSQL, Redis, the FastAPI runtime, and documented FinEvidence connectivity.
- Add health/readiness metadata, local configuration examples, integration checks, and recovery/fallback documentation.
- Keep the scope single-machine: no HA, clustering, Kubernetes, auth, or production operations.

## Capabilities

### New Capabilities

- `postgres-redis-local-runtime`: Run the durable Financial DeepResearch Runtime with PostgreSQL persistence and Redis queueing on one machine.

### Modified Capabilities

- None.

## Impact

- Backend persistence, worker queue, app factory, worker CLI, dependencies, tests, and README.
- Root Docker Compose and backend Dockerfile/configuration.
- No changes to FinEvidence code or its HTTP API.
