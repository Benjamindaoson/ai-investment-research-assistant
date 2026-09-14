## 1. Persistence and queue

- [x] 1.1 Add PostgreSQL dependency and implement the existing durable store contract with JSONB and lease semantics.
- [x] 1.2 Add Redis queue client and wire enqueue/worker consumption with database recovery fallback.
- [x] 1.3 Add environment-based backend selection and health metadata without breaking SQLite injection.

## 2. Local stack

- [x] 2.1 Add backend Dockerfile, root Docker Compose services, health checks, and safe local environment example.
- [x] 2.2 Update worker/API documentation for PostgreSQL, Redis, FinEvidence, and fresh local databases.

## 3. Verification

- [x] 3.1 Add PostgreSQL/Redis contract and configuration tests with service-gated integration coverage.
- [x] 3.2 Run the existing SQLite suite and static checks.
- [x] 3.3 Start the local PostgreSQL/Redis services and run real API enqueue/worker/read-back smoke. Full Compose runtime build remains blocked by Docker Hub image authorization in the current environment.
