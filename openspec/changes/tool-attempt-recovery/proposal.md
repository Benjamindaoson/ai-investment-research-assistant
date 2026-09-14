## Why

The runtime currently marks a task `RUNNING` before a provider call but has no durable record that the call was in flight. After a crash or lease loss, automatically retrying can duplicate an external effect whose outcome is unknown. A research system that claims durable recovery must make this ambiguity explicit and require a deliberate resolution.

## What Changes

- Add explicit `UNKNOWN_EFFECT` task, run, and tool-execution states.
- Persist a tool attempt before invoking the provider and update it only after the result is accepted.
- Block automatic takeover when an in-flight attempt has unknown outcome.
- Add an explicit operator resolution endpoint to authorize retry or mark the attempt failed.
- Preserve attempt identity and history across authorized retries.
- Update typed frontend contracts and read-only trace rendering for blocked/unknown attempts.

## Capabilities

### New Capabilities

- `tool-attempt-recovery`: Durable in-flight attempt state and explicit unknown-effect resolution.

### Modified Capabilities

## Impact

- Backend domain models, execution engine, API, persistence payloads, and tests.
- Frontend runtime schemas and tool trace presentation.
- No new dependency, no automatic provider retry, and no FinEvidence changes.
