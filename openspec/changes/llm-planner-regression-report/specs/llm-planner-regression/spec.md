## ADDED Requirements

### Requirement: LLM planner regression is explicit and configuration-gated

The regression runner SHALL require explicit LLM planner mode, an LLM API key, an LLM base URL/model, and a FinEvidence base URL for a live evaluation. It MUST NOT silently fall back to the deterministic planner when live configuration is missing.

#### Scenario: Missing live configuration is reported as blocked

- **WHEN** the runner is invoked without one or more required live configuration values
- **THEN** it writes a report with a blocked gate and exits non-zero without making a model call

#### Scenario: Configured live planner is invoked once

- **WHEN** all required live configuration is present
- **THEN** the runner invokes the configured LLM Planner Adapter once for the golden case and records provider/model metadata plus request and response hashes without recording credentials or raw response content

### Requirement: Plan quality is comparable to the deterministic baseline

The regression report SHALL include the deterministic baseline score, the LLM plan score, every plan check, task counts, dependency edges, and counter-evidence coverage for the same golden case.

#### Scenario: Structurally valid LLM plan passes the plan gate

- **WHEN** the LLM plan satisfies the existing planner evaluator
- **THEN** the report marks the plan gate PASS and includes the observed task contract metrics

#### Scenario: Invalid LLM plan remains visible as a failure

- **WHEN** the LLM plan is malformed or fails a golden-case check
- **THEN** the report records the provider/contract failure or failed checks and does not present the regression as passed

### Requirement: The accepted plan is evaluated through the live research runtime

The runner SHALL execute the LLM-generated plan through the existing FinEvidence HTTP provider and runtime engine, then report evidence qualification, claim linkage, thesis, memo status, memo section coverage, and artifact-link checks.

#### Scenario: Live run reaches a reviewable memo

- **WHEN** FinEvidence returns usable evidence and the runtime completes
- **THEN** the report includes the run state, provider coverage metadata, qualified evidence count, claim count, thesis presence, memo status, memo section keys, and run-evaluation checks

#### Scenario: Evidence or runtime is incomplete

- **WHEN** FinEvidence coverage is partial or the runtime fails before a complete memo
- **THEN** the report marks the relevant gate as PARTIAL, BLOCKED, or FAIL with the observed reason and preserves any available hashes/counts

### Requirement: Regression artifacts are secret-safe and reproducible

The report SHALL be JSON, contain the case hash and generated-at timestamp, and MUST NOT contain API keys, authorization headers, prompts, raw model responses, or unqualified claims of investment correctness.

#### Scenario: Report is inspected after execution

- **WHEN** the generated report is read back
- **THEN** it contains only serializable evaluation evidence and a scan of the report does not find the configured API key
