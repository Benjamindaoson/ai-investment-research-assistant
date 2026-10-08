"""Restartable local worker for persisted research runs."""

from __future__ import annotations

import argparse
import time
from pathlib import Path

from deepresearch.api import create_app
from deepresearch.persistence.store import SQLiteStore
from deepresearch.runtime.engine import ResearchEngine, RunLeaseConflictError, RunLeaseLostError
from deepresearch.runtime.queue import RedisRunQueue, RunQueue


def run_once(engine: ResearchEngine, queue: RunQueue | None = None) -> int:
    attempted = 0
    dispatched_id = queue.dequeue() if queue is not None else None
    runnable = engine.list_runnable_runs()
    if dispatched_id is not None:
        dispatched = next((run for run in runnable if run.id == dispatched_id), None)
        if dispatched is not None:
            runnable = [dispatched, *[run for run in runnable if run.id != dispatched_id]]
    for run in runnable:
        attempted += 1
        try:
            engine.execute(run.id)
        except (RunLeaseConflictError, RunLeaseLostError):
            continue
    return attempted


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Execute persisted Financial DeepResearch runs.")
    parser.add_argument("--database", type=Path, default=Path(".data/deepresearch.sqlite3"))
    parser.add_argument("--database-url", default=None, help="PostgreSQL DSN; overrides --database")
    parser.add_argument("--redis-url", default=None, help="Redis URL for dispatch consumption")
    parser.add_argument("--once", action="store_true", help="scan and execute runnable runs once")
    parser.add_argument("--poll-seconds", type=float, default=2.0)
    args = parser.parse_args(argv)
    if args.poll_seconds <= 0:
        parser.error("--poll-seconds must be positive")

    store: SQLiteStore
    if args.database_url:
        from deepresearch.persistence.postgres_store import PostgresStore

        store = PostgresStore(args.database_url)
    else:
        store = SQLiteStore(args.database)
    queue = RedisRunQueue(args.redis_url) if args.redis_url else None
    engine = create_app(store=store, run_queue=queue).state.research_engine
    if args.once:
        run_once(engine, queue)
        return 0
    while True:
        run_once(engine, queue)
        time.sleep(args.poll_seconds)


if __name__ == "__main__":
    raise SystemExit(main())
