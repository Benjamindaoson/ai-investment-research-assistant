## ADDED Requirements

### Requirement: Use the frozen FinEvidence v1 API

The production evidence provider MUST call only the configured FinEvidence v1
HTTP endpoints and MUST NOT call the retired `/v1/evidence/collect` endpoint or
import FinEvidence implementation modules.

#### Scenario: Task evidence is collected through v1

- GIVEN `FINEVIDENCE_BASE_URL` is configured
- WHEN a research task executes
- THEN the provider calls search, coverage, and citation under `/api/v1`
- AND it returns only validated runtime evidence records

### Requirement: Preserve external qualification

The provider MUST map FinEvidence coverage status and per-evidence verification
status into runtime qualification. The runtime MUST NOT promote a record that
FinEvidence left partial, unsupported, or unverified.

#### Scenario: Eligible supported evidence

- GIVEN coverage status is `ELIGIBLE`
- AND an evidence object has verification status `SUPPORTED`
- THEN the corresponding runtime record is `QUALIFIED`

#### Scenario: Partial or unsupported evidence

- GIVEN coverage status is not `ELIGIBLE`, or an evidence object is not
  `SUPPORTED`
- THEN the corresponding runtime record is `NEEDS_REVIEW`
- AND no synthetic record is created

### Requirement: Preserve citation provenance

Every emitted external record MUST retain the FinEvidence evidence ID,
document identity, page locator, source URL, verification metadata, and a
deterministic content hash. Invalid or incomplete citation responses MUST fail
the task explicitly.

#### Scenario: Citation is resolved

- GIVEN search returns an evidence ID
- WHEN the provider resolves its citation
- THEN the runtime record contains a non-empty source URL, locator, and hash

### Requirement: Fail explicitly at the transport boundary

The client MUST validate JSON and typed response contracts, bound each request
by a positive timeout, and surface HTTP, timeout, decode, and schema failures as
observable provider errors without falling back to deterministic evidence.

#### Scenario: FinEvidence is unavailable

- GIVEN a request times out or returns non-2xx
- THEN the task fails with `EvidenceProviderError`
- AND the runtime records a failed run rather than a successful tool execution
