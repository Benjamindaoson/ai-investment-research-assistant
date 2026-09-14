## ADDED Requirements

### Requirement: Research requirements preserve typed evidence semantics

The runtime SHALL represent each evidence requirement with validated fact type,
role, criticality, evidence role, and optional financial/source slots. Existing
requirements that omit the new fields SHALL remain valid through documented
defaults.

#### Scenario: Legacy requirement receives safe defaults

- **WHEN** a requirement contains only id, description, minimum_records, and
  required_stances
- **THEN** it validates as a retrieved, critical value requirement with a
  non-empty default role, leaves optional evidence role unset, and remains
  serializable in the existing plan format

#### Scenario: Invalid semantic value is rejected

- **WHEN** a requirement contains an unsupported fact type, criticality,
  evidence role, or blank semantic slot
- **THEN** domain validation fails before the plan is persisted

### Requirement: FinEvidence coverage consumes task-owned semantics

The HTTP evidence provider SHALL serialize each requirement's typed semantics
and available slots into the frozen `/api/v1/evidence/coverage` request. It
MUST use the research case target only when the requirement has no explicit
entity and MUST omit absent optional slots.

#### Scenario: Structured requirement reaches coverage

- **WHEN** an HTTP-backed task has metric, period, role, criticality, and
  evidence role fields
- **THEN** the coverage request contains those exact values under the matching
  FinEvidence requirement fields

#### Scenario: Requirement-specific entity overrides case target

- **WHEN** a requirement declares an entity different from the research case
  target
- **THEN** coverage uses the requirement entity without mutating the case

### Requirement: Live task contracts expose requirement semantics

The live runtime task contract SHALL parse and display structured requirement
metadata when present, while continuing to render historical requirements that
contain only the original fields.

#### Scenario: Reviewer sees semantic metadata

- **WHEN** a runtime task response includes typed requirement fields
- **THEN** the task contract displays fact type, role, criticality, and evidence
  role alongside the existing requirement description and stance

#### Scenario: Historical task remains readable

- **WHEN** a runtime task response omits the additive semantic fields
- **THEN** the UI renders the original requirement information without a parse
  or display error
