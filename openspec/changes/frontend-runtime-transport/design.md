# Design

The existing `ResearchRuntimeService` remains the only HTTP transport. Runtime
responses are parsed with Zod before reaching a repository caller. The frontend
financial input uses string decimals so precision is not lost in JavaScript;
the backend remains authoritative for computation.

The unconfigured service continues to fail explicitly rather than returning
synthetic runtime data. Synthetic design work remains behind the separate
`DefaultResearchRepository` and is not silently mixed with runtime responses.
