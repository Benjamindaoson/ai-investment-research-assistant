## ADDED Requirements

### Requirement: Run evaluation verifies memo structure

The deterministic run scorer SHALL require an `InvestmentMemo` with exactly one
non-empty section for each of `thesis`, `evidence`, `risks`, `scenarios`, and
`decision`.

#### Scenario: Valid structured memo

- **WHEN** a completed run contains all five non-empty memo sections
- **THEN** the scorer records a passing `memo_sections` check

#### Scenario: Missing memo section

- **WHEN** a run has no memo or is missing a required section
- **THEN** the scorer records a failing `memo_sections` check and the result does
  not pass

### Requirement: Run evaluation verifies memo artifact links

The scorer SHALL verify that memo section claim, evidence, and unresolved
requirement IDs refer only to artifacts present in the same run.

#### Scenario: Closed memo links

- **WHEN** all section links resolve to run artifacts
- **THEN** the scorer records a passing `memo_artifact_links` check

#### Scenario: Dangling memo link

- **WHEN** any memo section references an unknown claim or evidence ID
- **THEN** the scorer records a failing `memo_artifact_links` check
