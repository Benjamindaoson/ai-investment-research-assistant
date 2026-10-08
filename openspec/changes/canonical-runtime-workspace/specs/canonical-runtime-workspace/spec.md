## ADDED Requirements

### Requirement: Canonical live research entry point
The frontend SHALL use the durable Research Runtime for the primary new-research and research-case entry points whenever `NEXT_PUBLIC_RESEARCH_RUNTIME_URL` is configured.

#### Scenario: Start a real case from the primary entry point
- **WHEN** an analyst opens `/new-research` with the runtime URL configured and submits a target, question, and mandate
- **THEN** the browser creates a durable ResearchCase/ResearchRun through the typed runtime service and navigates to the run workspace

### Requirement: Backend-owned research output
The live workspace SHALL render run state, task progress, evidence qualification, claims, thesis, and memo data from validated runtime API responses.

#### Scenario: Completed run displays evidence and memo
- **WHEN** the backend run reaches a terminal state with evidence and a memo
- **THEN** the browser displays the observed evidence counts, qualification status, thesis/claims, and memo sections without creating replacement client-side facts

### Requirement: Existing route compatibility
The legacy research routes SHALL resolve to the canonical runtime workflow rather than silently executing fixture research.

#### Scenario: Existing research route is opened
- **WHEN** an analyst opens `/research` or `/research/{caseId}`
- **THEN** the application navigates to the runtime start page or the latest durable run for that case, and reports a clear error when the case is unavailable

### Requirement: Explicit local configuration
The frontend SHALL document the local runtime URL and SHALL show an explicit configuration error when it is absent.

#### Scenario: Runtime URL is missing
- **WHEN** the frontend is started without `NEXT_PUBLIC_RESEARCH_RUNTIME_URL`
- **THEN** the live research workspace remains visibly unconfigured and does not label fixture data as live runtime output
