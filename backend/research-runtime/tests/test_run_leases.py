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
