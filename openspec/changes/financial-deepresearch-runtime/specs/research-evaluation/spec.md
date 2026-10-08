## ADDED Requirements

### Requirement: Executable golden evaluation

The evaluation system SHALL load versioned cases and score runtime results against explicit state, evidence, claim, and abstention expectations.

#### Scenario: Score a passing case

- **WHEN** a completed run contains the required qualified evidence and linked claim types
- **THEN** the scorer SHALL return a passing EvaluationResult with per-check evidence

#### Scenario: Report unavailable capability honestly

- **WHEN** a case requires an unavailable external provider or dataset
- **THEN** the scorer SHALL report `N/A` or blocked checks and SHALL not manufacture a numeric success score
