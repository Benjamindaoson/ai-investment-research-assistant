## ADDED Requirements

### Requirement: Use the frozen FinEvidence configuration names

The runtime MUST select the HTTP evidence provider when
`FIN_EVIDENCE_BASE_URL` is set, and MUST prefer it over the legacy
`FINEVIDENCE_BASE_URL` alias.

#### Scenario: Canonical URL selects HTTP provider

- **WHEN** `FIN_EVIDENCE_BASE_URL` is set
- **THEN** application construction selects `HttpEvidenceProvider`
- **AND** the runtime does not select the deterministic provider

#### Scenario: Legacy URL remains compatible

- **WHEN** only `FINEVIDENCE_BASE_URL` is set
- **THEN** application construction selects `HttpEvidenceProvider`
- **AND** the compatibility behavior is documented

#### Scenario: Canonical URL wins

- **WHEN** both URL variables are set
- **THEN** the canonical `FIN_EVIDENCE_BASE_URL` value is used

### Requirement: Preserve explicit offline mode

The runtime MAY select the deterministic provider only when neither external URL
variable is configured, and documentation MUST identify that provider as local
synthetic data.

#### Scenario: Offline mode is explicit

- **WHEN** neither `FIN_EVIDENCE_BASE_URL` nor `FINEVIDENCE_BASE_URL` is set
- **THEN** application construction selects the deterministic provider
- **AND** runtime documentation identifies its evidence as local synthetic data
