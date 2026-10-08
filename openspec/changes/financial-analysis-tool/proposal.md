# Financial analysis tool

## Why

The runtime records tool executions but does not yet provide a deterministic
financial computation boundary. A research system cannot rely on model prose for
basic financial math.

## What changes

- Add typed financial snapshot and analysis result contracts.
- Implement a dependency-free calculator for common investment metrics.
- Expose the calculator through the runtime API with explicit unavailable metric
  semantics and input hashing.

## Out of scope

- Obtaining financial data, normalizing filings, or investment advice.
- Forecasting, valuation multiples, or scenario probabilities.
