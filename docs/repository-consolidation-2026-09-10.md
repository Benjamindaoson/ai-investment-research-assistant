# Repository Consolidation - 2026-09-10

This repository is the private canonical home for investment research product
work. The following public predecessors were audited and migrated here before
deletion:

| Source repository | Destination | Preserved assets |
| --- | --- | --- |
| `financial-research-assistant` | `legacy_imports/financial_research_assistant_v1/` | FastAPI backend, multi-agent research graph, memory modules, RAG prototype, config, tests, Vue frontend |
| `StockTitan` | `legacy_imports/stocktitan_v1/` | Java monitor service, AI engine, dashboard prototype, alerting/reporting code, RAG/backtesting design docs |
| `stock-monitor` | `legacy_imports/stock_monitor_v0/` | Earlier Java monitor service, README/docs, SQL schema/data snapshot |

Excluded material:

- `.git`, `.codegraph`, caches, virtual environments, build outputs, and local
  IDE files.
- Bundled Maven distributions and binary dependency archives.
- Runnable repository-level workflows from predecessors.

Operational note: these imports are preservation material only. They are not
wired into the current workspace, and no investment advice or trading action
boundary should be inferred from the predecessor code.
