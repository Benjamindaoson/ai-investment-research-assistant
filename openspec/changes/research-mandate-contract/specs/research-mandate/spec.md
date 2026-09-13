## ADDED Requirements

### Requirement: Research cases preserve an explicit mandate

The runtime MUST accept and persist a ResearchMandate containing decision type,
time horizon, materiality, required outputs, and constraints.

#### Scenario: Create a case with a mandate

- **WHEN** a client creates a research case with valid mandate fields
- **THEN** the case response and persisted case contain the same normalized mandate
- **AND** the generated plan records the mandate used for planning

#### Scenario: Omitted mandate uses stable defaults

- **WHEN** an older client creates a case without mandate fields
- **THEN** the runtime creates a valid case using documented defaults
- **AND** the case remains compatible with the canonical planner

### Requirement: Planner identity includes decision context

The runtime MUST include the normalized mandate in the planner input hash and
MUST reject a plan whose mandate does not match its ResearchCase.

#### Scenario: Different mandate changes planner identity

- **WHEN** two otherwise identical cases have different materiality or time horizon
- **THEN** their planner input hashes differ

#### Scenario: Mismatched plan is rejected

- **WHEN** a planner returns a plan with a mandate different from the case
- **THEN** runtime plan validation fails before the case or run is persisted
