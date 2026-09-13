## ADDED Requirements

### Requirement: Run review exposes validated plan context

The runtime workspace MUST display the planner identity and mandate of the
validated plan when the backend returns them.

#### Scenario: Display plan mandate

- **WHEN** a run response contains a validated plan with a mandate
- **THEN** the workspace displays decision type, time horizon, materiality, and
  required outputs
- **AND** it displays the planner identity and input hash

#### Scenario: Historical run without plan

- **WHEN** a compatible run response omits the plan field
- **THEN** the workspace continues to render execution state
- **AND** it labels plan context as unavailable rather than fabricating it
