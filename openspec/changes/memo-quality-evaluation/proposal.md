## Why

The runtime evaluation currently verifies execution and one claim link but does
not verify the memo artifact that analysts consume. A malformed or unlinked memo
could therefore pass the quality gate even when the runtime's stated product
boundary is broken.

## What Changes

- Add memo section completeness and artifact-link checks to `score_run`.
- Make the checks observable as named evaluation results rather than a single
  opaque boolean.
- Add a negative test proving a run with missing sections fails evaluation.

## Capabilities

### New Capabilities

- `memo-quality-evaluation`: Deterministic quality checks for structured memo
  output.

### Modified Capabilities

None.

## Impact

- Evaluation scorer and tests only; no runtime or API behavior change.
