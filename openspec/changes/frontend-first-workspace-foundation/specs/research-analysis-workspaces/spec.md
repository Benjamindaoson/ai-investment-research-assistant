## ADDED Requirements

### Requirement: Complete P0 research workflow routes
The application SHALL provide the complete P0 flow from New Research through setup, plan, execution, Research Case, Findings, Evidence Intelligence, Company Research, Thesis, Risk / Catalyst, monitoring, Human Review, Living Brief, Versioning, and basic Research Library using typed mock research data.

#### Scenario: Open a shared research context
- **WHEN** a user navigates among prototype workflow routes
- **THEN** each route SHALL retain the common shell and present research-specific content rather than a generic dashboard

### Requirement: Progressive research run experience
The Research Case route SHALL simulate staged research progress and progressively render findings during a mock run.

#### Scenario: Start a mock research run
- **WHEN** a user starts or restarts a research run
- **THEN** progress SHALL advance through planning, searching, reading, extracting evidence, analyzing, counter-evidence, human review, and completed stages

### Requirement: Evidence-first analysis views
Research analysis routes SHALL distinguish supporting evidence from counter evidence and expose source / citation context.

#### Scenario: Inspect selected claim context
- **WHEN** a user selects a claim or evidence item
- **THEN** the application SHALL display its verification state and source context in the context pane or drawer

### Requirement: Backend-replaceable frontend contracts
Every P0 domain read or mutation SHALL be represented by an explicit TypeScript service operation, runtime-validated at the repository boundary where external data enters the application.

#### Scenario: Replace mock transport later
- **WHEN** a future backend service implements the typed service interface
- **THEN** query hooks and UI components SHALL continue to use the same repository contracts without importing fixtures or transport implementations

### Requirement: Human-controlled research mutations
The mock product SHALL support plan edits, research run controls, evidence status changes, claim decisions, notes, thesis challenges, more-research requests, and brief approval with visible state and audit history.

#### Scenario: Review an AI-generated conclusion
- **WHEN** an analyst approves, rejects, edits, challenges, or requests more research
- **THEN** the affected workspace SHALL update and the Human Review history SHALL record the action as mock analyst activity

### Requirement: Living research continuity
The application SHALL represent Living Brief versions and explain changes in thesis, evidence, risk, and confidence between versions.

#### Scenario: Compare brief versions
- **WHEN** an analyst selects two available versions
- **THEN** the version workspace SHALL display a structured diff and a concise What Changed summary

### Requirement: Basic research library
The application SHALL expose uploaded files, reports, papers, company documents, evidence, and saved sources with search and filters for tags, company, industry, and source type.

#### Scenario: Narrow library results
- **WHEN** an analyst searches or applies a supported filter
- **THEN** the visible mock library items SHALL update while preserving source type and provenance metadata
