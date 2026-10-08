## 1. Regression runner

- [x] 1.1 Add a standalone runner that reads explicit LLM/FinEvidence configuration and fails closed when live configuration is missing.
- [x] 1.2 Reuse the existing planner and run scorers to produce baseline, LLM plan, and live runtime metrics.
- [x] 1.3 Write secret-safe JSON reports with hashes, gates, counts, and explicit failure semantics.

## 2. Verification and documentation

- [x] 2.1 Add unit tests for configuration gating, report redaction, and plan/run gate aggregation.
- [x] 2.2 Run one real configured planner regression against local FinEvidence and read the report back without exposing credentials.
- [x] 2.3 Run backend tests, lint, typecheck, compile checks, and OpenSpec validation; document the command and observed result.
