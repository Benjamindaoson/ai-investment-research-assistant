# Design

`FinancialAnalysisTool` is a pure deterministic service over a validated
`FinancialSnapshot`. It uses `Decimal` arithmetic and returns `None` for a
metric whose inputs are missing or mathematically undefined, recording that
metric in `unavailable_metrics`. Capex is treated as a positive cash outflow,
so free cash flow is operating cash flow minus capex.

The result stores a SHA-256 hash of the canonical input payload. It is an
analysis artifact, not evidence: source provenance remains owned by the
EvidenceProvider boundary and the caller must link this result to a task/tool
execution when it becomes part of a run.
