import os
from datetime import UTC, datetime
from uuid import uuid4

import pytest
from fastapi.testclient import TestClient

from deepresearch.api import create_app
from deepresearch.domain.models import ResearchCase
from deepresearch.persistence.store import SQLiteStore
from deepresearch.runtime.engine import ResearchEngine
from deepresearch.runtime.evidence import DeterministicEvidenceProvider
from deepresearch.runtime.queue import RedisRunQueue
from deepresearch.worker import run_once


class RecordingQueue:
    def __init__(self) -> None:
        self.items: list[str] = []

    def enqueue(self, run_id: str) -> None:
        if run_id not in self.items:
            self.items.append(run_id)

    def dequeue(self, timeout: int = 0) -> str | None:
        return self.items.pop(0) if self.items else None


def test_enqueue_uses_injected_queue_and_worker_consumes_it(tmp_path) -> None:
    queue = RecordingQueue()
    app = create_app(SQLiteStore(tmp_path / "runtime.sqlite3"), run_queue=queue)
    client = TestClient(app)
    created = client.post(
        "/api/v1/research-cases",
        json={"question": "Assess ACME durability", "target": "ACME"},
    )
    run_id = created.json()["run_id"]

    queued = client.post(f"/api/v1/research-runs/{run_id}/enqueue")

    assert queued.status_code == 202
    assert queue.items == [run_id]
    assert run_once(app.state.research_engine, queue) == 1
    assert client.get(f"/api/v1/research-runs/{run_id}").json()["state"] == "COMPLETED"
    assert client.get("/api/v1/health").json()["queue"] == "redis"


@pytest.mark.integration
def test_postgres_store_round_trip_when_configured() -> None:
    dsn = os.environ.get("POSTGRES_TEST_DSN")
    if not dsn:
        pytest.skip("set POSTGRES_TEST_DSN to run PostgreSQL integration smoke")
    from deepresearch.persistence.postgres_store import PostgresStore

    store = PostgresStore(dsn)
    suffix = uuid4().hex
    case_id = f"case-postgres-{suffix}"
    target = f"target-{suffix}"
    case = ResearchCase(id=case_id, question="Assess", target=target)
    run = ResearchEngine(store, DeterministicEvidenceProvider()).create_run(case)
    run_id = run.id
    store.append_event(run_id, "RUN_CREATED", {"case_id": case_id})
    checkpoint_id = store.save_checkpoint(run_id, {"state_version": 1})
    store.save_evaluation({"id": f"evaluation-{suffix}", "run_id": run_id, "passed": True})
    store.save_memory({"target": target, "latest_run_id": run_id, "updated_at": datetime.now(UTC).isoformat()})

    assert store.get_case(case_id)["target"] == target
    assert store.get_run(run_id)["state"] == "CREATED"
    assert any(event["event_type"] == "RUN_CREATED" for event in store.events(run_id))
    assert store.latest_checkpoint(run_id)["id"] == checkpoint_id
    assert store.latest_evaluation(run_id)["passed"] is True
    assert store.get_memory(target)["latest_run_id"] == run_id


@pytest.mark.integration
def test_redis_queue_deduplicates_dispatch_when_configured() -> None:
    url = os.environ.get("REDIS_TEST_URL")
    if not url:
        pytest.skip("set REDIS_TEST_URL to run Redis integration smoke")
    queue = RedisRunQueue(url, name=f"deepresearch:test:{uuid4().hex}")
    try:
        queue.enqueue("run-1")
        queue.enqueue("run-1")
        assert queue.dequeue() == "run-1"
        assert queue.dequeue() is None
    finally:
        queue.client.delete(queue.name, queue.pending_name)
        queue.close()
