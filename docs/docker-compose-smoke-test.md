# Docker Compose smoke test

This repository includes a small end-to-end smoke test for the active Financial DeepResearch runtime.

The smoke test starts the Docker Compose stack, waits for runtime readiness, then runs a complete research workflow over HTTP:

1. `GET /api/v1/ready`
2. create a research case
3. execute the run
4. submit evidence-linked financial analysis
5. submit valuation scenarios
6. submit a red-team review
7. submit all five IC reviews
8. record a chair decision
9. fetch the final memo and verify that it links reviews and valuation output

## Run the smoke test

From the repository root:

```bash
bash scripts/smoke-docker-compose.sh
```

By default the script:

- builds and starts `postgres`, `redis`, `runtime`, and `worker`
- exposes the runtime at `http://127.0.0.1:8011`
- runs `scripts/smoke_runtime.py`
- tears the stack down afterward, including volumes

## Keep services running after the test

```bash
SMOKE_KEEP_SERVICES=1 bash scripts/smoke-docker-compose.sh
```

Then stop them manually:

```bash
docker compose down --volumes --remove-orphans
```

## Use a different runtime port

```bash
RUNTIME_PORT=8021 bash scripts/smoke-docker-compose.sh
```

## Run against an already running runtime

```bash
RUNTIME_BASE_URL=http://127.0.0.1:8011 python scripts/smoke_runtime.py
```

## Run with API-key protection

If the runtime is configured with API keys, pass one to the smoke client:

```bash
DEEPRESEARCH_API_KEY=local-dev-key python scripts/smoke_runtime.py
```

The smoke client sends the key as `X-API-Key` when the environment variable is set.

## Expected output

A successful run prints a sequence similar to:

```text
ready: ok
created run: run-...
execute: completed
financial analysis: revenue growth 20.0%
valuation: valuation-...
red-team review: ok
ic reviews: ok
decision: decision-...
memo: memo-...
smoke: ok
```

## Notes

- The default Compose configuration uses deterministic planner, synthesizer, and evidence provider settings.
- No external LLM or evidence service is required for the default smoke test.
- The smoke script intentionally uses only the Python standard library.
