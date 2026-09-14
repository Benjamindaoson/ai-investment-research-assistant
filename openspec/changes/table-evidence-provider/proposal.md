## Why

Financial research often needs exact entity/metric/period table evidence, not a
lexical search result. The frozen FinEvidence v1 API already exposes this
capability, but the runtime has no registered data provider that can consume it
through the same durable task/evidence path.

## What Changes

- Add a table-backed HTTP evidence provider that uses FinEvidence's public
  `/api/v1/table/query` endpoint.
- Reuse the existing coverage, citation, provenance, and qualification
  boundary; do not parse TableIR or infer financial values.
- Register the provider as `financial-table` when the configured provider is
  the real FinEvidence HTTP provider.
- Preserve deterministic defaults and explicit registry injection behavior.
- Add unit and real-smoke coverage for table endpoint routing and identity.

## Capabilities

### New Capabilities

- `table-evidence-provider`: Exact table evidence is available as a registered
  Research Runtime data tool.

### Modified Capabilities

## Impact

- `backend/research-runtime/src/deepresearch/runtime/evidence.py` and runtime
  exports/factory wiring.
- Provider tests, integration smoke, and runtime documentation.
- No FinEvidence source changes, no direct internal imports, and no financial
  value inference.
