## ADDED Requirements

### Requirement: Red-team evidence traceability is evaluated

The deterministic run evaluator SHALL verify every Red-team review against the
evaluated run and thesis, and every cited evidence ID against a current-run
COUNTER or CONFLICTING evidence record. An invalid review or evidence link MUST
fail the named evaluation check.

#### Scenario: Valid Red-team review passes

- **WHEN** a Red-team review belongs to the run/current thesis and cites only
  current-run counter or conflicting evidence
- **THEN** the evaluator records a `red_team_links` PASS check

#### Scenario: Invalid Red-team link fails

- **WHEN** a review has a wrong owner, dangling evidence ID, or supporting-only
  evidence
- **THEN** the evaluator records a `red_team_links` FAIL check with sorted
  invalid IDs

### Requirement: Golden cases may require Red-team coverage

The evaluator SHALL support an optional `minimum_red_team_reviews`
golden-case field. When present, the observed valid review count MUST meet the
declared minimum; when absent, no coverage check is required.

#### Scenario: Minimum review count is met

- **WHEN** the valid Red-team review count is at least the declared minimum
- **THEN** the evaluator records a `red_team_coverage` PASS check

#### Scenario: Minimum review count is not met

- **WHEN** the valid Red-team review count is below the declared minimum
- **THEN** the evaluator records a `red_team_coverage` FAIL check and the
  golden case does not pass
