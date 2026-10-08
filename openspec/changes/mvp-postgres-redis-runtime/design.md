## Context

The runtime store currently writes JSON domain snapshots, append-only events, checkpoints, leases, evaluations, and investment memory through a small SQLite adapter. The worker currently scans those durable events. The MVP needs PostgreSQL and Redis, but existing unit tests must remain fast and independent of external services.

## Goals / Non-Goals

**Goals:**

- Preserve the existing store method contract and runtime semantics.
- Store the same JSON payloads in PostgreSQL with transactional writes and database leases.
- Push durable run IDs to Redis on enqueue and let the worker consume them, with a database scan fallback for recovery.
- Make `docker compose up --build` start a local runtime that is reachable from the browser and can connect to FinEvidence by URL.
- Keep SQLite as the default when no database URL is configured, so tests and lightweight development remain unchanged.

**Non-Goals:**

- No migration of an existing SQLite file into PostgreSQL in this MVP.
- No Redis Streams, Sentinel, Cluster, distributed locks, or exactly-once guarantees beyond the existing lease and event semantics.
- No production secret management or public network exposure.

## Decisions

1. Implement `PostgresStore` against the existing store contract using synchronous `psycopg` and JSONB payload columns. The domain model is already serialized as JSON and the MVP does not need relational projections; this avoids introducing an ORM and keeps the persistence boundary easy to compare with SQLite.

2. Implement `RedisRunQueue` with the standard Redis list operations. `ResearchEngine.enqueue` continues to append `RUN_ENQUEUED` first, then publishes the run ID. Worker consumption is an optimization for prompt dispatch; `list_runnable_runs()` remains the recovery source of truth after Redis loss or process restart.

3. Select backends in `create_app`: `RESEARCH_RUNTIME_DATABASE_URL` or `DATABASE_URL` selects PostgreSQL, and `RESEARCH_RUNTIME_REDIS_URL` selects Redis. Explicit `store`/`run_queue` injection remains available for tests. Health reports persistence and queue modes without exposing credentials.

4. Add a root `docker-compose.yml` with PostgreSQL, Redis, and runtime services. The runtime uses a local bind-mounted data directory only where useful; PostgreSQL uses a named volume and Redis is disposable for this MVP because queue intent remains in PostgreSQL events.

5. Keep the API process and worker process separate in Compose. Both point at the same PostgreSQL and Redis services, which proves that enqueue and execution work across process boundaries on one computer.

## Risks / Trade-offs

- [A second persistence adapter can drift from SQLite semantics] → Add contract tests for leases, events, checkpoints, memory, evaluations, and JSON round-trips; keep the shared engine unchanged.
- [Redis can be unavailable after an enqueue] → The enqueue event is written first and worker scan fallback recovers runnable runs from PostgreSQL.
- [Synchronous psycopg adds a dependency and native wheel] → Use `psycopg[binary]` in the backend environment and pin only a compatible major range.
- [Compose may not reach a host FinEvidence process on every OS] → Document `host.docker.internal` and allow deterministic mode when the external URL is absent.
