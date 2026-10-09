#!/usr/bin/env bash
set -euo pipefail

COMPOSE_PROJECT_NAME="${COMPOSE_PROJECT_NAME:-deepresearch-smoke}"
RUNTIME_PORT="${RUNTIME_PORT:-8011}"
export COMPOSE_PROJECT_NAME RUNTIME_PORT

cleanup() {
  if [[ "${SMOKE_KEEP_SERVICES:-0}" != "1" ]]; then
    docker compose down --volumes --remove-orphans
  fi
}
trap cleanup EXIT

echo "[smoke] starting docker compose stack on runtime port ${RUNTIME_PORT}"
docker compose up --build -d postgres redis runtime worker

echo "[smoke] running runtime workflow smoke test"
RUNTIME_BASE_URL="${RUNTIME_BASE_URL:-http://127.0.0.1:${RUNTIME_PORT}}" \
  python scripts/smoke_runtime.py

echo "[smoke] completed successfully"
