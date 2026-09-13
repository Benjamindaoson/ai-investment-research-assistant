# Investment memo output

## Why

The runtime currently ends at a thesis and decision record. The product wedge is
an evidence-backed investment memo that can be reproduced and reviewed later,
so the runtime needs a durable, explicitly review-gated memo projection.

## What changes

- Add a typed `InvestmentMemo` projection to `ResearchRun`.
- Generate its summary and evidence links from the run's qualified evidence,
  claims, thesis, and unresolved requirements.
- Expose a read-only memo endpoint and move its state to `APPROVED` only when a
  human approves the thesis.

## Out of scope

- Export formats, rich document editing, or LLM prose generation.
- Automatic investment recommendations or trade execution.
