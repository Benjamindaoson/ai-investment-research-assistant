## 1. Domain and attempt lifecycle

- [x] 1.1 Add `BLOCKED`/`UNKNOWN_EFFECT` state contracts, nullable completion time, and attempt key fields.
- [x] 1.2 Persist an unknown attempt before provider execution and close it on accepted success/failure.

## 2. Recovery and resolution

- [x] 2.1 Block takeover on unfinished attempts and synthesize safe legacy attempts.
- [x] 2.2 Add explicit retry/mark-failed resolution with preserved history and events.
- [x] 2.3 Add API error boundaries and update frontend runtime/tool trace schemas.

## 3. Verification

- [x] 3.1 Add tests for pre-call persistence, success/failure closure, lease loss, takeover blocking, legacy recovery, and both resolutions.
- [x] 3.2 Run backend/frontend tests, lint, typecheck, build, compileall, OpenSpec, CodeGraph, and Git checks.
