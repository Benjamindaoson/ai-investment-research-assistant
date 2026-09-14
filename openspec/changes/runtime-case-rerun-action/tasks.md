## 1. Typed rerun transport

- [x] 1.1 Add the existing-case run creation method to service and repository contracts.
- [x] 1.2 Add a mutation that invalidates case history and navigates after success.

## 2. Analyst action

- [x] 2.1 Add explicit create-run action with pending and error states to the history surface.
- [x] 2.2 Wire the action into the runtime workspace without automatic execution.

## 3. Verification

- [x] 3.1 Add transport, mutation, and component tests for success, pending, failure, and no execute side effect.
- [x] 3.2 Run frontend tests, lint, typecheck, build, backend regression, OpenSpec, CodeGraph, and Git checks.
