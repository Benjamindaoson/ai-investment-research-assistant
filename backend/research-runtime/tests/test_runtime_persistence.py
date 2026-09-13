from deepresearch.domain.models import ResearchCase
from deepresearch.persistence.store import SQLiteStore


def test_store_round_trip_and_append_only_events(tmp_path) -> None:
    store = SQLiteStore(tmp_path / "runtime.sqlite3")
    case = ResearchCase(id="case-1", question="Assess ACME's margin durability", target="ACME")
    store.save_case(case.model_dump(mode="json"))
    store.append_event("case-1", "CASE_CREATED", {"question": case.question})

    reopened = SQLiteStore(tmp_path / "runtime.sqlite3")
    assert reopened.get_case("case-1")["target"] == "ACME"
    assert reopened.events("case-1")[0]["event_type"] == "CASE_CREATED"


def test_checkpoint_read_back(tmp_path) -> None:
    store = SQLiteStore(tmp_path / "runtime.sqlite3")
    checkpoint_id = store.save_checkpoint("run-1", {"completed_task_ids": ["task-1"]})
    checkpoint = store.latest_checkpoint("run-1")
    assert checkpoint["id"] == checkpoint_id
    assert checkpoint["payload"]["completed_task_ids"] == ["task-1"]
