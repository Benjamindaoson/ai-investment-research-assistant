## ADDED Requirements

### Requirement: Memo sections are typed and evidence-linked

The runtime SHALL include a stable set of memo sections on every newly
generated `InvestmentMemo`. Each section MUST declare a supported key, non-empty
review body, and only IDs that exist in the run's claims, evidence, or unresolved
requirements.

#### Scenario: Fully qualified run produces review sections

- **WHEN** synthesis completes with all evidence requirements qualified
- **THEN** the memo contains `thesis`, `evidence`, `risks`, `scenarios`, and
  `decision` sections, and the memo remains `READY_FOR_REVIEW`

#### Scenario: Partial run exposes unresolved review work

- **WHEN** synthesis leaves at least one evidence requirement unresolved
- **THEN** the memo contains the same section keys, the affected sections link
  the unresolved requirement IDs, and the memo remains `DRAFT`

### Requirement: Section content cannot imply unsupported facts

The deterministic section generator SHALL derive body text from observed run
state and linked artifacts. It MUST NOT fabricate financial values, citations,
source records, or completion claims.

#### Scenario: No evidence is observed

- **WHEN** a run completes without qualified evidence
- **THEN** the sections explicitly report missing support and contain no
  fabricated positive or negative financial claim

### Requirement: Memo section transport is runtime validated

The backend memo response and frontend service schema SHALL validate the
structured sections before consumers use them.

#### Scenario: Malformed section response

- **WHEN** the frontend receives a memo section with an unsupported key or
  missing body
- **THEN** the service rejects the response at the schema boundary
