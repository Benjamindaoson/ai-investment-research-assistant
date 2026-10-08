## 1. Typed transport

- [x] 1.1 Add a runtime event schema, service method, and repository method for the existing events endpoint.
- [x] 1.2 Add query coverage for event loading and terminal-aware refresh behavior.

## 2. Audit surface

- [x] 2.1 Implement loading, empty, error, and populated read-only event trace states.
- [x] 2.2 Render the trace in the live runtime workspace without bypassing the repository boundary.

## 3. Verification

- [x] 3.1 Add transport, query, and component tests for valid, invalid, empty, and error event states.
- [x] 3.2 Run frontend tests, lint, typecheck, build, OpenSpec validation, and live runtime smoke verification.
