## ADDED Requirements

### Requirement: Runtime exposes an evidence-backed run trace

The Research Runtime API SHALL expose a stable trace summary for a run, including task completion, evidence qualification counts, provenance completeness, and claim-to-evidence links.

#### Scenario: Completed run exposes trace summary

- **WHEN** a client requests the trace for a completed run
- **THEN** the response includes the run ID, task IDs, evidence counts by qualification, provenance completeness counts, and every claim's evidence IDs

#### Scenario: Unknown run returns not found

- **WHEN** a client requests a trace for a run ID that is not persisted
- **THEN** the API returns HTTP 404 with a stable error detail

### Requirement: Frontend transport is replaceable by configuration

The frontend SHALL select a typed HTTP ResearchService only when explicitly configured with a runtime base URL, and SHALL retain the local synthetic service as the default development mode.

#### Scenario: Runtime URL selects HTTP service

- **WHEN** the frontend is built with a configured Research Runtime base URL
- **THEN** repository calls use the HTTP service and validate response data through the existing repository schemas

#### Scenario: No runtime URL selects synthetic service

- **WHEN** no runtime base URL is configured
- **THEN** repository calls use the explicitly labelled synthetic service and the UI remains runnable without a backend
