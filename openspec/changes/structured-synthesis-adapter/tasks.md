## 1. Structured synthesis contract

- [x] 1.1 Add strict synthesis draft models, provider protocol, deterministic adapter, and explicit LLM adapter.
- [x] 1.2 Validate model task/evidence links and keep runtime claim qualification/verification authoritative.

## 2. Runtime and API wiring

- [x] 2.1 Wire the configured synthesizer into `ResearchEngine` and preserve deterministic default behavior.
- [x] 2.2 Add explicit API configuration and provider error boundary without changing FinEvidence integration.

## 3. Verification

- [x] 3.1 Add backend tests for deterministic default, valid fake LLM response, malformed response, and evidence-link rejection.
- [x] 3.2 Run backend/frontend tests, lint, typecheck, build, compileall, OpenSpec, CodeGraph, and Git checks.
