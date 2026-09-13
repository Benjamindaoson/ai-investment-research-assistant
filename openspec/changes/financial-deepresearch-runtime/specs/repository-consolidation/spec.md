## ADDED Requirements

### Requirement: Single canonical application line

The repository SHALL contain one supported frontend, one supported backend/runtime, one canonical domain contract set, and one evaluation entry point.

#### Scenario: Inspect the supported tree

- **WHEN** a developer follows the root README
- **THEN** every supported run command SHALL point to `apps/web` or `backend/research-runtime`, and no legacy application SHALL be presented as runnable

### Requirement: Explicit legacy deletion policy

Historical, duplicate, demo-only, or third-party-derived implementations SHALL be deleted from the canonical branch when they have no supported caller or product ownership.

#### Scenario: Review rejected material

- **WHEN** a reviewer checks the consolidation audit
- **THEN** each deletion SHALL have a stated reason and each retained concept SHALL have a canonical destination
