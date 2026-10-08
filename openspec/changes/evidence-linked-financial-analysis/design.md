## Contract

The request contains a durable run ID, an explicit FinancialSnapshot, and a
mapping from snapshot metric names to FinEvidence evidence IDs:

    run_id
    snapshot.revenue = Decimal(...)
    evidence_ids.revenue = ["finevidence-id"]

The allowed mapping keys are the numeric snapshot fields:
revenue, prior_revenue, gross_profit, operating_income,
operating_cash_flow, capex, cash, and debt. The period is part of the
snapshot context and is not itself a numeric fact.

Every non-null numeric field MUST have a non-empty mapping. Every mapped ID
MUST exist in the run and have qualification QUALIFIED. The runtime does not
re-verify or re-rank evidence and does not parse table text.

## Result

FinancialAnalysisResult remains the calculation result and gains
evidence_ids, preserving the exact mapping used for the calculation. The
existing input hash continues to hash the snapshot values; the field-level
evidence mapping is separately available for audit.

## Failure semantics

The endpoint returns 404 for an unknown run, 422 for malformed or incomplete
links, and never returns a calculated result for an unqualified or missing
evidence reference.
