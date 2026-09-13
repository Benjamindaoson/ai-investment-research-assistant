## Why

The planner contract and structural evaluation baseline now exist, but the product cannot turn a natural-language investment question into a genuinely adaptive research plan until an LLM can propose structured tasks. The LLM must remain a replaceable proposal mechanism behind the already validated planner boundary; free-form model prose must never enter the runtime as truth.

## What Changes

- Add an OpenAI-compatible structured LLM planner adapter using the existing `ResearchPlanner` contract.
- Support DeepSeek or another compatible endpoint through environment configuration without storing or printing credentials.
- Require JSON task output, validate it as a ResearchPlan draft, and let the engine perform final case/hash/DAG/evidence validation.
- Record planner model/provider metadata and request/response hashes for audit and evaluation.
- Add explicit opt-in configuration and deterministic fallback behavior.
- Add mocked transport tests for valid output, malformed output, HTTP failure, timeout, and missing configuration.
- Keep live model calls out of the default test and development path.

## Capabilities

### New Capabilities

- `llm-research-planner`: Structured, configurable LLM proposal adapter with explicit failure semantics.

### Modified Capabilities

None.

## Impact

- Backend planner module, API configuration, tests, and documentation.
- Uses Python standard-library HTTP and hashing; no new dependency.
- External model calls are opt-in and require user-provided environment configuration.
- No change to FinEvidence ownership or evidence retrieval.
