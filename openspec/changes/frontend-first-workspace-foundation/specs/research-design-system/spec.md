## ADDED Requirements

### Requirement: Research design tokens
The application SHALL define reusable tokens for colors, typography, spacing, radii, shadows, borders, surfaces, motion, density, focus, hover, and selected states.

#### Scenario: Component state presentation
- **WHEN** an interactive component receives pointer, keyboard focus, selected, disabled, loading, or error state
- **THEN** it SHALL communicate that state through the shared token system with a visible focus indicator

### Requirement: Reusable research presentation components
The application SHALL provide reusable status, progress, finding, claim, evidence, thesis, source, activity, and context-drawer components.

#### Scenario: Render evidence status
- **WHEN** a screen renders supporting or counter evidence
- **THEN** the evidence component SHALL show its source, citation metadata, content excerpt, and semantic verification status
