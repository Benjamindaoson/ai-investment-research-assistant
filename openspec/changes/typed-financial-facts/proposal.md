## Why

Financial analysis currently accepts a snapshot and a separate evidence-link
map, but it does not preserve the typed fact contract that produced each
snapshot field. FinEvidence v1 intentionally returns evidence and provenance,
not an untrusted numeric answer, so the runtime needs an explicit handoff
between evidence-qualified extraction and deterministic financial calculation.

## What Changes

- Add a typed financial fact and fact-set contract with explicit value,
  period, unit, currency, basis, and evidence IDs.
- Build `FinancialSnapshot` only from that validated contract; reject duplicate
  fields, mixed periods, missing revenue, and invalid non-negative fields.
- Add a Research Run API that consumes the fact set, requires every linked
  evidence record to exist and be qualified, runs the existing calculation
  ledger, and persists the typed facts with the analysis artifact.
- Keep raw FinEvidence text out of numeric conversion; no implicit parsing,
  estimation, or fallback values.

## Capabilities

### New Capabilities

- `typed-financial-facts`: Evidence-linked, explicit financial facts can be
  converted into a calculation-ready snapshot.

### Modified Capabilities

## Impact

- Backend domain models, financial mapping, runtime API, persistence payloads,
  and tests.
- No FinEvidence source changes, no direct internal imports, no new
  dependencies, and no frontend changes in this phase.
