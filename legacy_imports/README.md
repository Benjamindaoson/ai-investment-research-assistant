# Legacy Imports

This directory preserves predecessor assets that should not remain as separate
public repositories.

These imports are intentionally isolated from the active product runtime. Reuse
requires a separate review for data provenance, API credentials, runtime
dependencies, and investment-advice boundaries.

## 2026-09-10 Imports

- `financial_research_assistant_v1/` preserves the earlier FastAPI, multi-agent
  research workflow, memory modules, RAG prototype, and Vue frontend.
- `stocktitan_v1/` preserves the StockTitan-derived monitor, Java service,
  alerting, RAG/backtesting notes, and Python AI engine. Bundled Maven tools,
  build outputs, and binary dependencies were excluded.
- `stock_monitor_v0/` preserves the smaller stock monitor predecessor,
  including Java service code and its SQL snapshot for schema/data reference.

The canonical ongoing project is `ai-investment-research-assistant`.
