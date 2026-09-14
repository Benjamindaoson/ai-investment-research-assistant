## Why

The runtime has a real LLM Planner Adapter, but its current evidence is limited to contract tests. We need one reproducible, secret-safe regression that measures model-generated task contracts against the deterministic planner contract and then verifies the generated plan through the existing live FinEvidence-to-Memo runtime.

## What Changes

- Add a one-command LLM Planner regression runner using the configured OpenAI-compatible environment variables.
- Score the LLM plan and deterministic baseline with the existing planner evaluator.
- Execute the LLM-generated plan against the configured FinEvidence HTTP service using an isolated local store.
- Score evidence qualification, claim linkage, thesis/memo production, and memo artifact links.
- Write a JSON report containing hashes, metrics, gate results, and explicit blocked/N/A states without storing credentials or raw model responses.
- Document the command, required environment, and interpretation of the report.

## Capabilities

### New Capabilities

- `llm-planner-regression`: Run and persist a comparable, secret-safe LLM Planner and live runtime evaluation artifact.

### Modified Capabilities

- None.

## Impact

- A new backend evaluation runner and report artifact under `backend/research-runtime/evaluation/`.
- Reuses the existing planner, FinEvidence HTTP provider, runtime engine, and evaluation scorer; no new model SDK or FinEvidence dependency.
- Requires an explicitly configured LLM endpoint and local FinEvidence service for a live run.
