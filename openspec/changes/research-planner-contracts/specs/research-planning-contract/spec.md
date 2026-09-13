## ADDED Requirements

### Requirement: Research plans preserve planner provenance

The runtime SHALL represent a research plan with a stable ID, case ID, question input hash, planner name, planner version, validation status, and the complete task contract that was proposed.

#### Scenario: Deterministic plan is persisted

- **WHEN** a new case is created without explicit tasks
- **THEN** the runtime creates a validated plan with planner identity, input hash, and evidence-bearing tasks before creating the run

#### Scenario: Plan can be read independently

- **WHEN** a client requests the plan for a persisted run
- **THEN** the API returns the plan metadata and task contracts without requiring execution to have started

### Requirement: Planner output is replaceable

The runtime SHALL depend on a `ResearchPlanner` contract rather than a concrete planning algorithm, and the deterministic implementation MUST be explicitly identified as non-LLM local planning.

#### Scenario: Custom planner can supply tasks

- **WHEN** the engine is constructed with a planner implementation
- **THEN** run creation uses that planner output and persists its planner identity and version

#### Scenario: Planner output is invalid

- **WHEN** a planner returns a cyclic DAG or a task without evidence requirements
- **THEN** run creation rejects the output before persisting the case or run
