## ADDED Requirements

### Requirement: The bounded fallback plan must declare semantic evidence intent

The deterministic planner MUST retain the three-task market/fundamentals/risk
DAG while emitting non-generic evidence requirements for the target entity.

#### Scenario: Financial plan contains aligned requirements

- **WHEN** a research case is planned by the deterministic planner
- **THEN** the fundamentals requirement is a critical retrieved fact with
  `VALUE_SUPPORT` evidence role for the case target
- **AND** the risk requirement is a critical counter-evidence requirement for
  the case target
- **AND** the market requirement identifies explanatory/context support for the
  case target.

### Requirement: Planner remains bounded and question-specific slots stay honest

The deterministic planner MUST NOT invent metric, period, currency, unit, or
financial values that are not present in the research case.

#### Scenario: Missing financial slots remain unset

- **WHEN** the question does not state a specific metric or period
- **THEN** the generated requirements leave those optional slots unset
- **AND** the plan remains valid under the existing DAG and planner evaluator.
