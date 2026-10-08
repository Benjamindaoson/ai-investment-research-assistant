# Design

The live workspace uses the existing runtime repository and TanStack Query
hooks. The runtime service validates only the fields needed by this screen,
while the backend remains authoritative for task state, evidence, claims, and
memo content. Mutations replace the cached run rather than maintaining a
second client-side state machine.

CORS defaults to local development origins and can be overridden with a
comma-separated environment variable. No wildcard origin is introduced.
