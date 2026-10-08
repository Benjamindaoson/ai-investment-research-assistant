## Context

`FinancialAnalysisResult` currently contains calculated values, an input hash, and field-level evidence IDs. That is enough to reject unlinked inputs, but not enough for a reviewer to reproduce an individual metric without inferring the implementation from source code. The runtime already uses `Decimal` and deterministic serialization, so the change can extend the existing contract without a new calculation engine or dependency.

The ledger must remain a runtime-owned calculation artifact. FinEvidence supplies qualified evidence; it does not execute or explain the investment model's arithmetic.

## Goals / Non-Goals

**Goals:**

- Produce one stable ledger entry for each metric the financial tool evaluates.
- Make available and unavailable results equally inspectable.
- Keep formulas and normalized inputs deterministic and safe to render.
- Preserve the existing `input_hash` and evidence ID mapping.
- Persist and expose the ledger through the existing financial-analysis API and runtime UI.

**Non-Goals:**

- No arbitrary user-supplied expression execution.
- No valuation model, forecast engine, market-data adapter, or currency conversion.
- No changes to FinEvidence endpoints or implementation.
- No replacement of the existing financial-analysis result fields; the ledger explains them.

## Decisions

1. **Use a typed `CalculationLedgerEntry` value object.**

   Each entry contains `metric`, `formula`, `inputs`, `value`, `unit`, `status`, and an optional `reason`. `inputs` are serialized decimal strings, while `value` is nullable for unavailable metrics. This keeps the artifact JSON-safe and avoids floating-point drift.

   Alternative rejected: storing free-form calculation text only. Text would be readable but not reliably machine-checkable or comparable across runs.

2. **Generate entries in the existing `FinancialAnalysisTool`.**

   The current formulas remain the single source of truth. The tool emits the result field and the matching ledger entry in the same calculation path, so a result cannot silently diverge from its audit record.

   Alternative rejected: reconstructing the ledger in the API or frontend. That duplicates financial logic and makes the audit surface untrustworthy.

3. **Represent missing and undefined calculations explicitly.**

   A zero denominator, absent prior period, or missing cash-flow input creates an `UNAVAILABLE` entry with a reason. The existing `unavailable_metrics` list remains for compatibility and is derived from the same entries.

4. **Expose the ledger read-only.**

   The existing financial-analysis response and runtime trace carry the persisted entries. The frontend renders formula, inputs, output, unit, and status; it does not recalculate values.

5. **Keep backward reads tolerant.**

   Historical analysis artifacts without `calculation_ledger` deserialize as an empty ledger. Newly generated artifacts always include the complete ledger. This avoids a destructive migration of existing SQLite runs.

## Risks / Trade-offs

- [Risk] Existing persisted runs do not have ledger entries → Mitigation: use a default empty list and label the UI as unavailable for historical artifacts.
- [Risk] Formula text can become stale if arithmetic changes → Mitigation: generate formula and inputs adjacent to each calculation and test both numeric output and ledger content.
- [Risk] A ledger may imply more financial validity than the inputs deserve → Mitigation: retain evidence IDs, provenance, and explicit unavailable states; the ledger documents arithmetic, not source truth.

## Migration Plan

No database migration is required because run payloads are JSON serialized and Pydantic defaults missing ledger fields. Deploy code and frontend together; rollback is safe because older clients ignore the additional response field and newer clients tolerate absent historical entries.

## Open Questions

None for this slice. Forecasting, valuation, and currency-aware calculations require a separate product decision and contract.
