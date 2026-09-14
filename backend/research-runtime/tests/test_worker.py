from fastapi.testclient import TestClient

from deepresearch.api import create_app
from deepresearch.persistence.store import SQLiteStore
from deepresearch.runtime.engine import ResearchEngine
from deepresearch.worker import run_once


def test_enqueue_and_worker_complete_a_persisted_run(tmp_path) -> None:
    store = SQLiteStore(tmp_path / "runtime.sqlite3")
    app = create_app(store)
    client = TestClient(app)
    created = client.post("/api/v1/research-cases", json={"question": "Assess ACME durability", "target": "ACME"})
    run_id = created.json()["run_id"]

    queued = client.post(f"/api/v1/research-runs/{run_id}/enqueue")
    attempted = run_once(app.state.research_engine)

    assert queued.status_code == 202
    assert queued.json() == {"run_id": run_id, "state": "CREATED", "queued": True}
    assert attempted == 1
    assert client.get(f"/api/v1/research-runs/{run_id}").json()["state"] == "COMPLETED"
    assert any(event["event_type"] == "RUN_ENQUEUED" for event in client.get(f"/api/v1/research-runs/{run_id}/events").json())


def test_worker_resumes_interrupted_run_without_reexecuting_completed_tasks(tmp_path) -> None:
    store = SQLiteStore(tmp_path / "runtime.sqlite3")
    app = create_app(store)
    client = TestClient(app)
    created = client.post("/api/v1/research-cases", json={"question": "Assess ACME durability", "target": "ACME"})
    run_id = created.json()["run_id"]
    engine: ResearchEngine = app.state.research_engine
    partial = engine.execute(run_id, stop_after_tasks=1)
    before = len(partial.tool_executions)

    assert run_once(engine) == 1
    resumed = engine.get_run(run_id)

    assert partial.state == "RUNNING"
    assert resumed.state == "COMPLETED"
    assert len(resumed.tool_executions) == 3
    assert before == 1
    assert run_once(engine) == 0
    assert len(engine.get_run(run_id).tool_executions) == 3


def test_worker_leaves_a_leased_run_untouched(tmp_path) -> None:
    store = SQLiteStore(tmp_path / "runtime.sqlite3")
    app = create_app(store)
    client = TestClient(app)
    created = client.post("/api/v1/research-cases", json={"question": "Assess ACME durability", "target": "ACME"})
    run_id = created.json()["run_id"]
    assert client.post(f"/api/v1/research-runs/{run_id}/enqueue").status_code == 202
    assert store.acquire_run_lease(run_id, "other-worker", 60)

    assert run_once(app.state.research_engine) == 1
    assert client.get(f"/api/v1/research-runs/{run_id}").json()["state"] == "CREATED"


def test_worker_does_not_execute_an_unqueued_run(tmp_path) -> None:
    store = SQLiteStore(tmp_path / "runtime.sqlite3")
    app = create_app(store)
    client = TestClient(app)
    created = client.post("/api/v1/research-cases", json={"question": "Assess ACME durability", "target": "ACME"})
    run_id = created.json()["run_id"]

    assert run_once(app.state.research_engine) == 0
    assert client.get(f"/api/v1/research-runs/{run_id}").json()["state"] == "CREATED"
