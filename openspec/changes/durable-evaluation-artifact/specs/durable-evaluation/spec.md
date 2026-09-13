## ADDED Requirements

### Requirement: Evaluation results are run-bound artifacts
The runtime SHALL bind each persisted run evaluation to the evaluated `run_id`, `case_id`, evaluator identity, and a stable hash of the supplied evaluation case.

#### Scenario: Evaluation records its basis
- **WHEN** a run is evaluated against a golden case
- **THEN** the result includes the run ID, case ID, evaluator identity, and case hash alongside named checks

#### Scenario: Mismatched case is rejected
- **WHEN** an evaluation case ID does not match the run's research case ID
- **THEN** evaluation is rejected without persisting an artifact or evaluation event

### Requirement: Evaluation artifacts are durable and readable
The runtime SHALL persist complete evaluation results and SHALL return the latest artifact for a run without recomputing it.

#### Scenario: Evaluation survives reconstruction
- **WHEN** an evaluation is recorded and a new engine/store instance reads the run
- **THEN** the latest evaluation contains the same checks, metadata, and pass state

#### Scenario: Multiple evaluations preserve history
- **WHEN** a run is evaluated more than once
- **THEN** each artifact remains stored and the read path returns the newest artifact

### Requirement: Evaluation semantics remain honest
Durable evaluation SHALL reuse the existing deterministic scorer and preserve explicit `N/A` or blocked outcomes for unavailable external capabilities; it MUST NOT infer success from model self-report.

#### Scenario: External capability remains unscored
- **WHEN** a golden case requires an unavailable external provider
- **THEN** the persisted result preserves the scorer's `N/A` outcome and does not manufacture a numeric pass
