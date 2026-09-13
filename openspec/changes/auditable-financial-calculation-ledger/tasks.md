## 1. Domain and calculation implementation

- [x] 1.1 Add the typed `CalculationLedgerEntry` contract with explicit status, decimal inputs, output, unit, and unavailable reason.
- [x] 1.2 Extend `FinancialAnalysisResult` with a backward-compatible calculation ledger field.
- [x] 1.3 Generate deterministic ledger entries from the existing `FinancialAnalysisTool` for growth, margins, free cash flow, and net cash.
- [x] 1.4 Keep `unavailable_metrics`, `input_hash`, and evidence ID mappings consistent with the generated ledger.

## 2. API and frontend audit surface

- [x] 2.1 Expose and validate the ledger through the existing financial-analysis API and run persistence without changing endpoint semantics.
- [x] 2.2 Extend the frontend runtime contract and render the ledger as read-only calculation provenance.
- [x] 2.3 Render historical results without a ledger as explicitly unavailable rather than fabricated.

## 3. Verification

- [x] 3.1 Add backend tests for stable hashes, formulas, available metrics, missing inputs, zero denominators, negative free cash flow, and evidence-linked persistence.
- [x] 3.2 Add frontend contract and component tests for available and unavailable ledger entries.
- [x] 3.3 Run backend tests, lint, typecheck, compileall, frontend tests, typecheck, lint, build, OpenSpec, CodeGraph, and Git checks; confirm FinEvidence remains untouched.
