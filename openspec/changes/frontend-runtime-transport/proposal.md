# Frontend runtime transport

## Why

The Next.js app already has a typed Research Runtime trace boundary, but the
memo, target memory, and deterministic financial analysis contracts are not
available to the frontend. Without these methods the UI cannot consume the
canonical runtime even when a runtime URL is configured.

## What changes

- Add Zod-validated service methods for runtime memo, investment memory, and
  financial analysis.
- Expose those methods through `ResearchRuntimeRepository` with transport tests.
- Preserve explicit unconfigured/synthetic behavior and repository ownership of
  the service boundary.

## Out of scope

- Replacing all synthetic workspace fixtures in one pass.
- Client-side financial calculations or direct page-level fetches.
