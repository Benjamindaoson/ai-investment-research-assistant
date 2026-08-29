## ADDED Requirements

### Requirement: Desktop research workspace shell
The application SHALL render a desktop-first shell with global top bar, primary navigation rail, a main workspace area, and an optional context pane.

#### Scenario: Navigate a primary workspace
- **WHEN** a user activates a primary navigation item
- **THEN** the application SHALL navigate to its route and visually mark that item selected

#### Scenario: Narrow viewport
- **WHEN** available viewport width is below the desktop shell breakpoint
- **THEN** the context pane and navigation SHALL remain accessible in overlay drawers without obscuring the main route permanently

### Requirement: Keyboard command palette
The application SHALL provide a keyboard-operable command palette opened by Cmd/Ctrl+K.

#### Scenario: Open and close command palette
- **WHEN** a user presses Cmd/Ctrl+K and then Escape
- **THEN** the palette SHALL open with a focusable search control and subsequently close with focus restored to its trigger

### Requirement: Shared asynchronous route states
The application SHALL provide route-level loading and error surfaces that use the application design system.

#### Scenario: Route loading
- **WHEN** an asynchronous route segment is pending
- **THEN** the application SHALL display a research-oriented skeleton instead of a blank screen
