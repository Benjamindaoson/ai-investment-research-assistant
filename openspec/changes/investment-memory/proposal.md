# Investment memory projection

## Why

Institutional research repeats over the same company or asset. The runtime
currently persists each run independently, but has no durable target-level view
of prior theses, memos, decisions, and unresolved requirements.

## What changes

- Add a durable `InvestmentMemory` projection keyed by research target.
- Update it after synthesis and human decisions, retaining version references
  rather than copying an unbounded transcript.
- Expose a read endpoint for the latest target-level research context.

## Out of scope

- Knowledge graphs, GraphRAG, vector search, or automatic thesis reinterpretation.
- Cross-tenant memory policy, which requires production identity and storage.
