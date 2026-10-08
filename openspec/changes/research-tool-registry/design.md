## Context

The runtime has one `EvidenceProvider` dependency and the planner emits a
`tool_name` per task. The current engine ignores that name for dispatch, so
provider substitution is possible only by replacing the entire engine
dependency. The next product boundary is a registry that keeps orchestration
in the runtime and makes tool selection explicit without creating an agent
swarm.

## Goals / Non-Goals

**Goals:**

- Resolve task tool names through a deterministic, in-memory registry.
- Keep `ResearchEngine(store, provider)` source-compatible for existing users.
- Make unknown tools fail with the existing durable attempt and failure event.
- Select the same resolved provider for qualification and claim verification.

**Non-Goals:**

- No dynamic plugin loading, dependency injection framework, or network
  discovery.
- No new financial calculation or table-query tool in this change.
- No automatic fallback from an unknown tool to another provider.

## Decisions

1. **Use a mapping-backed registry.** `ResearchToolRegistry` owns a mapping from
   non-blank names to providers and exposes `resolve`/`collect`. Duplicate names
   are impossible in a mapping; blank names and providers without callable
   `collect` are rejected at construction.

2. **Keep a compatibility constructor.** When no registry is supplied, the
   engine builds a registry mapping the existing task aliases
   (`deterministic-research`, `external-evidence`, `research`, and
   `evidence.search`) to the supplied provider. This preserves current callers
   while making the default canonical names explicit. A caller that supplies a
   registry gets strict unknown-tool behavior.

3. **Resolve per task.** The engine resolves the provider before calling
   `collect`; the selected provider name is written to the receipt. Unknown
   names use `unregistered` in the receipt and then fail through the ordinary
   provider error path.

4. **Use task resolution for downstream gates.** Qualification and optional
   claim verification resolve the task's provider rather than consulting one
   global provider. This prevents a multi-provider run from applying the wrong
   authority or verifier.

## Risks / Trade-offs

- [Compatibility aliases are broad] → They are limited to existing names and
  can be removed only in a breaking contract change.
- [Registry is process-local] → It is deterministic and testable; persistent
  tool catalog/versioning is deferred until tools become independently
  deployable.
- [Unknown tools fail at execution] → The run and receipt remain auditable,
  while plan creation stays compatible with external planners that may use
  names not yet deployed.
