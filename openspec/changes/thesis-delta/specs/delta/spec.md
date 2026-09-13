## ADDED Requirements

### Requirement: Subsequent research creates an observed thesis delta

The runtime SHALL compare a new target run with the previous latest run using
only persisted evidence and requirement state, and SHALL retain both thesis
references.

#### Scenario: New run has less qualified evidence

- **WHEN** a subsequent run has fewer qualified records than the previous run
- **THEN** memory exposes a negative qualified-evidence delta and identifies the
  previous and current thesis IDs

#### Scenario: Previous run is unavailable

- **WHEN** the previous latest run cannot be read or validated
- **THEN** the runtime leaves the delta absent rather than fabricating a change

### Requirement: Delta does not masquerade as confidence

The delta summary SHALL identify its values as observed count changes and SHALL
not present them as model confidence, return prediction, or investment advice.

#### Scenario: Delta is read back

- **WHEN** an analyst reads target memory
- **THEN** the latest delta includes explicit metric names and the non-confidence
  boundary in its summary
