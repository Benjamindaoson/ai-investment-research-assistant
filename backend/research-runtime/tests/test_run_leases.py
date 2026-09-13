from deepresearch.persistence.store import SQLiteStore


def test_run_lease_allows_one_owner_and_matching_release_only(tmp_path) -> None:
    store = SQLiteStore(tmp_path / "runtime.sqlite3")

    assert store.acquire_run_lease("run-1", "lease-1", 60)
    assert not store.acquire_run_lease("run-1", "lease-2", 60)
    assert not store.release_run_lease("run-1", "wrong-lease")
    assert not store.acquire_run_lease("run-1", "lease-3", 60)
    assert store.release_run_lease("run-1", "lease-1")
    assert store.acquire_run_lease("run-1", "lease-2", 60)


def test_expired_lease_is_reclaimed_and_stale_owner_cannot_release(monkeypatch, tmp_path) -> None:
    now = [100.0]
    monkeypatch.setattr("deepresearch.persistence.store.time.time", lambda: now[0])
    store = SQLiteStore(tmp_path / "runtime.sqlite3")

    assert store.acquire_run_lease("run-1", "lease-1", 5)
    now[0] = 106.0
    assert store.acquire_run_lease("run-1", "lease-2", 5)
    assert not store.release_run_lease("run-1", "lease-1")
    assert store.release_run_lease("run-1", "lease-2")


def test_lease_renewal_requires_current_owner_and_extends_expiry(monkeypatch, tmp_path) -> None:
    now = [100.0]
    monkeypatch.setattr("deepresearch.persistence.store.time.time", lambda: now[0])
    store = SQLiteStore(tmp_path / "runtime.sqlite3")

    assert store.acquire_run_lease("run-1", "lease-1", 5)
    now[0] = 104.0
    assert store.renew_run_lease("run-1", "wrong", 10) is False
    assert store.renew_run_lease("run-1", "lease-1", 10) is True
    now[0] = 108.0
    assert store.acquire_run_lease("run-1", "lease-2", 5) is False
    now[0] = 115.0
    assert store.acquire_run_lease("run-1", "lease-2", 5) is True


def test_owned_writes_reject_stale_token(tmp_path) -> None:
    store = SQLiteStore(tmp_path / "runtime.sqlite3")
    payload = {"id": "run-1", "case_id": "case-1", "state": "CREATED"}
    store.save_run(payload)
    assert store.acquire_run_lease("run-1", "lease-1", 60)

    assert store.save_run_owned({**payload, "state": "RUNNING"}, "wrong") is False
    assert store.append_event_owned("run-1", "wrong", "STALE", {}) is False
    assert store.save_checkpoint_owned("run-1", "wrong", {"state_version": 2}) is None
    assert store.save_run_owned({**payload, "state": "RUNNING"}, "lease-1") is True
    assert store.append_event_owned("run-1", "lease-1", "OWNED", {}) is True
    assert store.save_checkpoint_owned("run-1", "lease-1", {"state_version": 2}) is not None


def test_owned_memory_write_requires_current_lease_and_supports_insert(tmp_path) -> None:
    store = SQLiteStore(tmp_path / "runtime.sqlite3")
    store.save_run({"id": "run-1", "case_id": "case-1", "state": "CREATED"})
    memory = {"target": "ACME", "updated_at": "2026-09-14T00:00:00+00:00"}

    assert store.save_memory_owned(memory, "run-1", "wrong") is False
    assert store.acquire_run_lease("run-1", "lease-1", 60)
    assert store.save_memory_owned(memory, "run-1", "lease-1") is True
    assert store.save_memory_owned({**memory, "updated_at": "2026-09-14T00:01:00+00:00"}, "run-1", "lease-1") is True
    assert store.get_memory("ACME")["updated_at"] == "2026-09-14T00:01:00+00:00"
