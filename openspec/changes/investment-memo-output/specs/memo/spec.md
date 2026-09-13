## ADDED Requirements

### Requirement: A run produces a durable evidence-linked memo projection

The runtime SHALL persist an `InvestmentMemo` on synthesis, including the run,
thesis, claim, qualified evidence, counter/conflicting evidence, and unresolved
requirement identifiers.

#### Scenario: Fully qualified run

- **WHEN** all task evidence requirements qualify
- **THEN** the run contains a `READY_FOR_REVIEW` memo whose evidence IDs exist in
  the run and whose unresolved requirement list is empty

#### Scenario: Partially qualified run

- **WHEN** at least one evidence requirement remains unresolved
- **THEN** the run contains a `DRAFT` memo with the unresolved requirement IDs
  visible and no fabricated completion claim

### Requirement: Memo approval requires human thesis approval

The runtime SHALL only set a memo to `APPROVED` through an explicit human
`APPROVE_THESIS` decision for a completed run.

#### Scenario: Human approves completed thesis

- **WHEN** an analyst approves the run thesis
- **THEN** the linked memo becomes `APPROVED`

#### Scenario: Run is incomplete

- **WHEN** an analyst attempts to approve a thesis for a non-completed run
- **THEN** the decision is rejected and the memo remains unapproved
