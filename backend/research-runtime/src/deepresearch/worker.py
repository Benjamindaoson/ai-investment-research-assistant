"""Restartable local worker for persisted research runs."""

from __future__ import annotations

import argparse
import time
from pathlib import Path

from deepresearch.api import create_app
from deepresearch.persistence.store import SQLiteStore
from deepresearch.runtime.engine import ResearchEngine, RunLeaseConflictError


def run_once(engine: ResearchEngine) -> int:
    attempted = 0
    for run in engine.list_runnable_runs():
        attempted += 1
        try:
            engine.execute(run.id)
        except RunLeaseConflictError:
            continue
    return attempted


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Execute persisted Financial DeepResearch runs.")
    parser.add_argument("--database", type=Path, default=Path(".data/deepresearch.sqlite3"))
    parser.add_argument("--once", action="store_true", help="scan and execute runnable runs once")
    parser.add_argument("--poll-seconds", type=float, default=2.0)
    args = parser.parse_args(argv)
    if args.poll_seconds <= 0:
        parser.error("--poll-seconds must be positive")

    engine = create_app(store=SQLiteStore(args.database)).state.research_engine
    if args.once:
        run_once(engine)
        return 0
    while True:
        run_once(engine)
        time.sleep(args.poll_seconds)


if __name__ == "__main__":
    raise SystemExit(main())
