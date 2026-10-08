## Why

FinancialAnalysisTool currently computes transparent Decimal metrics, but its
input is detached from the research run that supplied the financial facts.
That makes a correct calculation difficult to audit and leaves room for a
caller to attach arbitrary evidence after the fact.

## What Changes

- Add a field-level evidence link contract for financial analysis.
- Require every supplied numeric snapshot field to reference at least one
  qualified evidence record from the same durable research run.
- Persist the field-to-evidence mapping in the analysis result and keep the
  existing Decimal calculation semantics.
- Expose a run-scoped API endpoint and typed frontend repository method.
- Reject unknown metric keys, missing links, unknown evidence IDs, and
  unqualified evidence explicitly.

## Non-goals

- No parsing of arbitrary table text or reimplementation of TableIR.
- No invention of missing financial values.
- No changes to FinEvidence.

## Impact

- Financial domain result, runtime API, and frontend service boundary.
- Existing manual financial-analysis endpoint remains backward-compatible but
  is not evidence-backed.
