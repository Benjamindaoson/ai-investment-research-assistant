## 1. Verification receipt contract

- [x] 1.1 Add backward-compatible operation and verification-result fields to
  `ToolExecution`.
- [x] 1.2 Thread lease context through synthesis and persist verification
  attempt start, success, negative result, and failure transitions.

## 2. Runtime and frontend surface

- [x] 2.1 Extend the frontend runtime receipt schema for verification metadata.
- [x] 2.2 Render verification operation and supported result in the existing
  read-only tool trace without raw payloads.

## 3. Verification

- [x] 3.1 Add backend tests for pre-call persistence, supported and unsupported
  results, bounded provider failure, and legacy receipt compatibility.
- [x] 3.2 Add frontend receipt rendering coverage and update runtime
  documentation.
- [x] 3.3 Run backend/frontend tests, lint, typecheck, build, OpenSpec,
  CodeGraph, and Git read-back checks.
