## ADDED Requirements

### Requirement: Real adapter smoke must observe evidence

The integration smoke MUST require the frozen FinEvidence search endpoint to
return at least one evidence object before validating identity, citation, and
qualification fields.

#### Scenario: Search returns real evidence

- **WHEN** the smoke runs with `FIN_EVIDENCE_INTEGRATION=1` and a reachable
  `FIN_EVIDENCE_BASE_URL`
- **THEN** the health response is `ok`
- **AND** the search response contains at least one runtime evidence record
- **AND** each observed record preserves the FinEvidence evidence ID, document
  ID, citation identity, source URL, page locator, content hash, and provider
  identity.

### Requirement: The runtime HTTP API must complete an external run

The integration smoke MUST exercise the runtime HTTP boundary with FinEvidence
configured and MUST verify that the completed run is backed by external
evidence rather than the deterministic fixture provider.

#### Scenario: Create and execute a live research run

- **WHEN** the smoke creates an HSBC research case through
  `POST /api/v1/research-cases`
- **AND** executes the returned run through
  `POST /api/v1/research-runs/{run_id}/execute`
- **THEN** runtime health reports `LIVE_EXTERNAL` and `finevidence-http`
- **AND** the run completes with non-empty evidence
- **AND** every returned evidence record has complete FinEvidence provenance
- **AND** the memo is `READY_FOR_REVIEW`
- **AND** the event stream contains a terminal completion event.

### Requirement: External integration remains explicit and bounded

The default test suite MUST NOT require a running FinEvidence service, and the
smoke MUST NOT require a non-empty table result for a broad query.

#### Scenario: Offline default and empty table response

- **WHEN** the integration environment variables are absent
- **THEN** the external smoke is skipped
- **AND** table lookup with no matching rows remains a valid empty result.
