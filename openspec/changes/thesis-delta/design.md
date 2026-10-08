# Design

When a new memo is synthesized, the runtime loads the previous latest run from
SQLite and compares only observed fields: qualified evidence count,
counter/conflicting evidence count, and unresolved requirement count. The
result stores both thesis IDs and a deterministic summary that explicitly says
it is not a confidence estimate.

Only the latest delta is indexed on `InvestmentMemory`; historical runs remain
the source of truth and preserve the full audit trail. If the previous run is
missing or cannot be validated, no delta is fabricated.
