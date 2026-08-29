## ADDED Requirements

### Requirement: Research workflow prototype routes
The application SHALL provide Company Research, Research Case, Research Matrix, Signal Review, and Living Brief routes based on typed mock research data.

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
