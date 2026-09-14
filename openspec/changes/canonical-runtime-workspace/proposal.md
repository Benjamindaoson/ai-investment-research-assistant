## Why

The application already has a durable PostgreSQL-backed Research Runtime, but the primary `/new-research` and `/research` entry points still use synthetic fixtures. That makes the visible product diverge from the actual evidence-first runtime and prevents a browser user from completing the real create → run → evidence → memo journey.

## What Changes

- Make the durable Research Runtime the canonical frontend research workspace.
- Route the existing research entry points to the runtime case/run workflow.
- Preserve a typed HTTP boundary for case creation, enqueue/start, progress polling, evidence, claims, thesis, and memo output.
- Add an application-level live configuration example for `NEXT_PUBLIC_RESEARCH_RUNTIME_URL`.
- Add browser/API acceptance coverage for the real PostgreSQL-backed runtime path.
- Keep the old mock services available only for unrelated legacy screens until those screens are separately migrated.

## Capabilities

### New Capabilities

- `canonical-runtime-workspace`: The primary frontend research workflow uses the durable Research Runtime and renders its evidence-qualified output.

### Modified Capabilities

## Impact

- Next.js route entry points and runtime workspace navigation.
- Frontend environment documentation and browser smoke coverage.
- No new backend dependency, no FinEvidence changes, and no client-side persistence.
