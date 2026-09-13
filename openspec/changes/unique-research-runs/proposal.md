## Why

`ResearchRun` currently derives its ID solely from `ResearchCase`, so a second
run for the same case overwrites the first run and its events/checkpoints. That
breaks durable recovery and makes Investment Memory unable to retain genuine
run history.

## What Changes

- Generate a unique ID for every newly created `ResearchRun`.
- Preserve the case ID link and all existing run endpoint behavior.
- Add a regression test proving two runs for one case remain independently
  readable and executable.

## Capabilities

### New Capabilities

- `unique-research-runs`: Independent durable run identities per case.

### Modified Capabilities

None.

## Impact

- Runtime run creation and execution tests.
- Run IDs returned by the API become opaque unique identifiers; no persistence
  migration is required for existing rows.
