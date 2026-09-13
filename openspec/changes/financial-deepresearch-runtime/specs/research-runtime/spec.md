## ADDED Requirements

### Requirement: Durable research case contract

The runtime SHALL validate and persist a research case, its run, tasks, evidence requirements, claims, thesis, decisions, tool executions, checkpoints, and append-only events using versioned domain contracts.

#### Scenario: Create a research case

- **WHEN** a caller submits a non-empty financial research question and scope
- **THEN** the runtime SHALL return a stable case and run identifier, persist the initial state, and append a case-created event

#### Scenario: Reject invalid terminal state

- **WHEN** a caller submits a terminal run without a completion timestamp or a task without required fields
- **THEN** contract validation SHALL fail before persistence

### Requirement: Dependency-aware research execution

The runtime SHALL execute a validated ResearchTask DAG in dependency order and SHALL record each ToolExecution and task transition.

#### Scenario: Execute ready tasks

- **WHEN** a run contains independent ready tasks and a dependent task
- **THEN** independent tasks SHALL execute before the dependent task, and the event log SHALL preserve that order

#### Scenario: Refuse cyclic plans

- **WHEN** a submitted plan contains a dependency cycle
- **THEN** the runtime SHALL reject the plan with a validation error and SHALL not start execution

### Requirement: Evidence qualification before synthesis

The runtime SHALL qualify evidence against its EvidenceRequirement and SHALL link every synthesized claim to one or more qualified EvidenceRecord values.

#### Scenario: Synthesize supported and counter claims

- **WHEN** a provider returns supporting and counter evidence for a task
- **THEN** the runtime SHALL persist both stances and produce claims whose evidence links preserve the stance and provenance

#### Scenario: Abstain without sufficient evidence

- **WHEN** required evidence is missing, conflicting, or unavailable
- **THEN** the runtime SHALL produce a partial or needs-review outcome and SHALL not mark the thesis as approved

### Requirement: Checkpoint and recovery

The runtime SHALL save a checkpoint after each durable task transition and SHALL resume from the latest valid checkpoint without duplicating completed tool executions.

#### Scenario: Resume an interrupted run

- **WHEN** execution stops after a completed task and is resumed
- **THEN** the runtime SHALL read back the checkpoint, skip the completed task, execute remaining ready tasks, and append a recovery event

### Requirement: FinEvidence boundary

The runtime SHALL consume evidence through a provider interface and SHALL keep evidence infrastructure ownership outside the application runtime.

#### Scenario: Use a deterministic local provider

- **WHEN** the local demo provider is configured
- **THEN** the runtime SHALL return explicitly marked deterministic evidence with source identity and retrieval metadata

### Requirement: Auditable human decision

The runtime SHALL record human review decisions separately from model-generated claims and SHALL preserve the actor, decision, target, rationale, and timestamp.

#### Scenario: Approve a thesis

- **WHEN** an analyst approves a thesis with a rationale
- **THEN** the runtime SHALL append a decision record and transition only the thesis review state, without rewriting the underlying evidence
