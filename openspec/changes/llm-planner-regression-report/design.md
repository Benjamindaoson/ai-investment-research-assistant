## Context

`LLMResearchPlanner` already validates structured model output and records request/response hashes. The deterministic planner evaluator already checks task coverage, dependency edges, evidence requirements, counter-evidence, task bounds, and duplicate tasks. The runtime can execute a plan through the frozen FinEvidence HTTP boundary and produce claims, thesis, and memo artifacts.

The missing piece is a repeatable bridge from a configured real model to a comparable report. The run must be safe to execute on a developer machine and must not copy API credentials or raw provider responses into the repository.

## Goals / Non-Goals

**Goals:**

- Use the existing OpenAI-compatible planner contract and environment configuration.
- Compare the LLM plan to the deterministic planner on the same golden case.
- Execute the LLM plan with live FinEvidence when configured.
- Evaluate the resulting run using existing deterministic run checks.
- Produce a stable JSON artifact with model/provider metadata, hashes, counts, gates, and failure semantics.

**Non-Goals:**

- Add a Gemini-native SDK or a second planner protocol in this change.
- Store prompts, raw model responses, API keys, or generated secrets.
- Change planner, evidence, synthesis, or persistence domain contracts.
- Treat a successful model call as evidence that the investment conclusion is correct.

## Decisions

- Use a standalone Python runner rather than a production API route. This keeps paid evaluation explicit and prevents accidental model calls from normal application startup.
- Reuse `score_plan` and `score_run` instead of creating a parallel scoring framework. The report records each check so failures remain inspectable.
- Use an isolated SQLite store by default for the evaluation execution. PostgreSQL/Redis remain the product runtime path; the evaluation runner must not pollute the user's durable workspace.
- Require `DEEPRESEARCH_PLANNER=llm`, configured LLM credentials, and `FIN_EVIDENCE_BASE_URL` for the live path. Missing configuration produces a blocked report and non-zero exit rather than silently switching to deterministic behavior.
- Persist only JSON-serializable summaries, hashes, and metrics. Provider secrets are read from the process environment and never enter report provenance.

## Risks / Trade-offs

- [Model/provider drift] → Record provider URL, model name, request/response hashes, and timestamp; interpret results as one observed regression, not a permanent model guarantee.
- [FinEvidence catalog coverage] → Preserve external coverage status and mark blocked/partial gates explicitly rather than upgrading unavailable evidence.
- [Paid call or timeout] → Execute one bounded planner call; preserve the failure reason and exit non-zero without retry loops.
- [Planner output is structurally valid but financially weak] → Keep semantic investment judgment outside the planner score and require downstream evidence/memo gates.
