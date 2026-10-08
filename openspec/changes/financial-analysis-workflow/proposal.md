## Why

The runtime already supports evidence-linked financial analysis, but the live
workspace only displays an artifact after it exists. An analyst currently has
no first-class way to submit explicit financial inputs and select the
qualified evidence that supports each field.

## What Changes

- Add a compact financial analysis form to the live run workspace.
- Require period, revenue, and revenue evidence; make prior revenue optional
  as a paired value and evidence selection.
- Use only qualified evidence from the loaded ResearchRun.
- Submit through the existing typed repository and update the run projection.
- Surface validation, loading, success, and failure states accessibly.

## Capabilities

### New Capabilities

- financial-analysis-workflow: Submit explicit evidence-linked financial
  analysis from the runtime workspace.

### Modified Capabilities

## Impact

Frontend runtime query hooks, workspace UI, repository tests, and UI styles
only. The backend contract and FinEvidence boundary are reused unchanged.
