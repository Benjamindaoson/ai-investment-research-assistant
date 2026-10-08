## ADDED Requirements

### Requirement: Real FinEvidence integration is explicitly verifiable

The runtime SHALL provide an opt-in integration smoke that calls only the
frozen FinEvidence v1 HTTP boundary and validates the evidence-to-citation
identity chain when the service is configured.

#### Scenario: Configured service returns evidence

- **WHEN** `FIN_EVIDENCE_INTEGRATION=1` and `FIN_EVIDENCE_BASE_URL` points to a
  reachable FinEvidence v1 service
- **THEN** the smoke exercises health, search, coverage, citation resolution,
  and `EvidenceRecord` conversion and validates identity/provenance invariants

#### Scenario: Catalog is empty or coverage is partial

- **WHEN** the service responds successfully with no matching evidence or
  `PARTIAL` coverage
- **THEN** the smoke preserves that observed result and does not claim the
  research requirement is eligible

#### Scenario: Integration is not enabled

- **WHEN** the opt-in environment flag is absent
- **THEN** the integration test is skipped and the default unit suite performs
  no network call
