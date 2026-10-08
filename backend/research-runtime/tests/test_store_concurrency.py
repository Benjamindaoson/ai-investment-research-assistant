from datetime import UTC, datetime

from deepresearch.persistence.store import SQLiteStore


def _run_payload(state: str) -> dict[str, object]:
    now = datetime.now(UTC).isoformat()
    return {
        "id": "run-1",
        "case_id": "case-1",
        "state": state,
        "tasks": [
            {
                "id": "task-1",
                "title": "Task",
                "purpose": "Collect evidence",
                "depends_on": [],
                "tool_name": "deterministic-evidence",
                "state": "PENDING",
                "evidence_requirements": [
                    {"id": "req-1", "description": "Need evidence", "minimum_records": 1}
                ],
            }
        ],
        "tool_executions": [],
        "evidence": [],
        "claims": [],
        "thesis": None,
        "memo": None,
        "financial_analysis": None,
        "valuation_scenarios": None,
        "red_team_reviews": [],
        "ic_reviews": [],
        "decisions": [],
        "checkpoint": None,
        "state_version": 1,
        "created_at": now,
        "updated_at": now,
        "completed_at": now if state in {"COMPLETED", "PARTIAL", "FAILED", "CANCELLED"} else None,
    }


def test_leased_writer_cannot_overwrite_a_cancelled_run(tmp_path) -> None:
    store = SQLiteStore(tmp_path / "runtime.sqlite3")
    store.save_run(_run_payload("RUNNING"))
    assert store.acquire_run_lease("run-1", "worker-lease", 60)

    store.save_run(_run_payload("CANCELLED"))

    assert not store.save_run_owned(_run_payload("COMPLETED"), "worker-lease")
    assert store.get_run("run-1")["state"] == "CANCELLED"


def test_leased_writer_can_rewrite_cancelled_as_cancelled_idempotently(tmp_path) -> None:
    store = SQLiteStore(tmp_path / "runtime.sqlite3")
    store.save_run(_run_payload("CANCELLED"))
    assert store.acquire_run_lease("run-1", "worker-lease", 60)

    assert store.save_run_owned(_run_payload("CANCELLED"), "worker-lease")
    assert store.get_run("run-1")["state"] == "CANCELLED"
