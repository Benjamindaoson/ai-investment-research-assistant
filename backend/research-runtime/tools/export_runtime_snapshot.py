"""Export one persisted ResearchRun and its audit events as JSON for local reporting."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from deepresearch.persistence.postgres_store import PostgresStore


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--database-url", required=True)
    parser.add_argument("--run-id", required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    store = PostgresStore(args.database_url)
    payload = store.get_run(args.run_id)
    if payload is None:
        raise SystemExit(f"run not found: {args.run_id}")
    output = {"case": store.get_case(payload["case_id"]), "run": payload, "events": store.events(args.run_id)}
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(output, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({"run_id": args.run_id, "output": str(args.output)}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
