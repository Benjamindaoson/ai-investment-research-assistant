## Why

The runtime correctly blocks a memo when external claim verification is incomplete, but the current trace does not explain which claim, evidence coverage, or verifier result caused the block. The product also exposes only Markdown export, leaving analysts without a readable investment report artifact.

## What Changes

- Expose claim verification receipts with evidence qualification, FinEvidence coverage status, verifier result, and evidence gaps.
- Tighten synthesis instructions and runtime validation so claims cite task-scoped, qualified evidence and use cautious language when support is incomplete.
- Add a deterministic-vs-LLM comparison report for the same FinEvidence endpoint/catalog observation.
- Add a local PDF investment memo exporter with provenance, thesis, claims, risks, evidence quality, and review status.

## Capabilities

### New Capabilities

- `claim-verification-explainability`: Make claim verification outcomes and evidence gaps inspectable through trace/report data.
- `investment-report-export`: Export a durable run into a human-readable PDF investment memo.

### Modified Capabilities

- None.

## Impact

- Backend runtime trace and synthesis validation.
- Local evaluation/comparison artifacts.
- Optional PDF tooling for single-machine analyst delivery; no production document service.
