## 1. Ownership-checked persistence

- [x] 1.1 Add SQLite lease renewal and ownership-checked run, checkpoint, and event writes.
- [x] 1.2 Add store tests for successful renewal, stale-token rejection, and guarded-write rejection.

## 2. Runtime heartbeat and recovery

- [x] 2.1 Add a bounded heartbeat around execution with explicit `RunLeaseLostError` handling.
- [x] 2.2 Recover persisted `RUNNING` tasks after lease takeover and preserve checkpoint semantics.
- [x] 2.3 Include release and heartbeat-loss flags in the lease lifecycle events and API error boundary.

## 3. Verification

- [x] 3.1 Add engine tests for slow-provider renewal, lease loss, stale-write prevention, and takeover recovery.
- [x] 3.2 Run backend tests, lint, typecheck, compileall, OpenSpec, CodeGraph, Git checks, and confirm FinEvidence remains untouched.
