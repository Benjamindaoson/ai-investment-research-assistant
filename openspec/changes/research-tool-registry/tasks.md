## 1. Registry contract

- [x] 1.1 Add a mapping-backed `ResearchToolRegistry` with provider validation,
  strict resolution, and compatibility aliases.
- [x] 1.2 Export the registry through the runtime package and wire it into the
  application factory without changing FinEvidence boundaries.

## 2. Engine dispatch

- [x] 2.1 Resolve each task tool before collection and persist selected provider
  identity in the existing execution receipt.
- [x] 2.2 Route qualification and claim verification through the task's
  resolved provider; make unknown tools fail with bounded diagnostics.

## 3. Verification

- [x] 3.1 Add tests for registry validation, provider selection, compatibility
  aliases, unknown-tool failure, and provider-specific qualification.
- [x] 3.2 Update runtime documentation and run backend/frontend tests, lint,
  typecheck, build, OpenSpec, CodeGraph, and Git checks.
