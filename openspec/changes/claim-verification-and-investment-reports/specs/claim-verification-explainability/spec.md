## ADDED Requirements

### Requirement: Claim verification outcomes are explainable

The runtime trace SHALL expose each claim's verification status, verifier receipt, cited evidence qualification, FinEvidence coverage status, and bounded evidence gaps.

#### Scenario: Unsupported claim is inspected

- **WHEN** a verifier returns `supported=false` for a claim
- **THEN** the trace identifies the claim, cited evidence, coverage statuses, verifier result, result hash, and a human-readable reason that the claim remains `NEEDS_REVIEW`

#### Scenario: Verification transport fails

- **WHEN** a verifier transport or contract error occurs
- **THEN** the trace exposes the failed receipt type, bounded diagnostic, error hash, and run failure state without exposing credentials or raw authorization data

### Requirement: Synthesized claims remain task-scoped and evidence-grounded

The runtime SHALL reject synthesis claims that cite evidence from another task and SHALL instruct structured synthesizers to make only claims directly supported by cited qualified evidence.

#### Scenario: Cross-task evidence is submitted

- **WHEN** a synthesis draft cites evidence belonging to a different task
- **THEN** synthesis fails with an explicit task-scope error and the run does not become a successful completed run

#### Scenario: Evidence support is incomplete

- **WHEN** a claim has no qualified supporting evidence or external verification returns unsupported
- **THEN** the claim remains `NEEDS_REVIEW` and the run/memo retain `PARTIAL`/`DRAFT` semantics
