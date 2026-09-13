"""Small transactional SQLite adapter for local durable runtime state."""

from __future__ import annotations

import json
import sqlite3
import time
from collections.abc import Iterator
from contextlib import contextmanager
from datetime import UTC, datetime
from pathlib import Path
from typing import Any
from uuid import uuid4


class SQLiteStore:
    def __init__(self, path: Path) -> None:
        self.path = path
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self._initialize()

    def _connect(self) -> sqlite3.Connection:
        connection = sqlite3.connect(self.path)
        connection.row_factory = sqlite3.Row
        connection.execute("PRAGMA foreign_keys = ON")
        return connection

    @contextmanager
    def _transaction(self) -> Iterator[sqlite3.Connection]:
        connection = self._connect()
        try:
            with connection:
                yield connection
        finally:
            connection.close()

    def _initialize(self) -> None:
        with self._transaction() as connection:
            connection.executescript(
                """
                CREATE TABLE IF NOT EXISTS cases (id TEXT PRIMARY KEY, payload TEXT NOT NULL);
                CREATE TABLE IF NOT EXISTS runs (id TEXT PRIMARY KEY, case_id TEXT NOT NULL, payload TEXT NOT NULL);
                CREATE TABLE IF NOT EXISTS events (
                    seq INTEGER PRIMARY KEY AUTOINCREMENT,
                    run_id TEXT NOT NULL,
                    event_type TEXT NOT NULL,
                    payload TEXT NOT NULL,
                    occurred_at TEXT NOT NULL
                );
                CREATE TABLE IF NOT EXISTS checkpoints (
                    id TEXT PRIMARY KEY,
                    run_id TEXT NOT NULL,
                    payload TEXT NOT NULL,
                    created_at TEXT NOT NULL
                );
                CREATE TABLE IF NOT EXISTS run_leases (
                    run_id TEXT PRIMARY KEY,
                    lease_id TEXT NOT NULL,
                    acquired_at TEXT NOT NULL,
                    expires_at REAL NOT NULL
                );
                CREATE TABLE IF NOT EXISTS investment_memory (
                    target TEXT PRIMARY KEY,
                    payload TEXT NOT NULL,
                    updated_at TEXT NOT NULL
                );
                """
            )

    def acquire_run_lease(self, run_id: str, lease_id: str, ttl_seconds: float) -> bool:
        if ttl_seconds <= 0:
            raise ValueError("ttl_seconds must be positive")
        now = time.time()
        with self._transaction() as connection:
            connection.execute("DELETE FROM run_leases WHERE expires_at <= ?", (now,))
            try:
                connection.execute(
                    "INSERT INTO run_leases(run_id, lease_id, acquired_at, expires_at) VALUES (?, ?, ?, ?)",
                    (run_id, lease_id, datetime.now(UTC).isoformat(), now + ttl_seconds),
                )
            except sqlite3.IntegrityError:
                return False
        return True

    def release_run_lease(self, run_id: str, lease_id: str) -> bool:
        with self._transaction() as connection:
            cursor = connection.execute(
                "DELETE FROM run_leases WHERE run_id = ? AND lease_id = ?",
                (run_id, lease_id),
            )
        return cursor.rowcount == 1

    def renew_run_lease(self, run_id: str, lease_id: str, ttl_seconds: float) -> bool:
        if ttl_seconds <= 0:
            raise ValueError("ttl_seconds must be positive")
        now = time.time()
        with self._transaction() as connection:
            cursor = connection.execute(
                """UPDATE run_leases SET expires_at = ?
                WHERE run_id = ? AND lease_id = ? AND expires_at > ?""",
                (now + ttl_seconds, run_id, lease_id, now),
            )
        return cursor.rowcount == 1

    def save_case(self, payload: dict[str, Any]) -> None:
        with self._transaction() as connection:
            connection.execute(
                "INSERT INTO cases(id, payload) VALUES (?, ?) ON CONFLICT(id) DO UPDATE SET payload=excluded.payload",
                (payload["id"], json.dumps(payload)),
            )

    def get_case(self, case_id: str) -> dict[str, Any] | None:
        with self._transaction() as connection:
            row = connection.execute("SELECT payload FROM cases WHERE id = ?", (case_id,)).fetchone()
        return json.loads(row["payload"]) if row else None

    def save_run(self, payload: dict[str, Any]) -> None:
        with self._transaction() as connection:
            connection.execute(
                """INSERT INTO runs(id, case_id, payload) VALUES (?, ?, ?)
                ON CONFLICT(id) DO UPDATE SET case_id=excluded.case_id, payload=excluded.payload""",
                (payload["id"], payload["case_id"], json.dumps(payload)),
            )

    def save_run_owned(self, payload: dict[str, Any], lease_id: str) -> bool:
        now = time.time()
        with self._transaction() as connection:
            cursor = connection.execute(
                """UPDATE runs SET case_id = ?, payload = ?
                WHERE id = ? AND EXISTS (
                    SELECT 1 FROM run_leases
                    WHERE run_id = ? AND lease_id = ? AND expires_at > ?
                )""",
                (payload["case_id"], json.dumps(payload), payload["id"], payload["id"], lease_id, now),
            )
        return cursor.rowcount == 1

    def get_run(self, run_id: str) -> dict[str, Any] | None:
        with self._transaction() as connection:
            row = connection.execute("SELECT payload FROM runs WHERE id = ?", (run_id,)).fetchone()
        return json.loads(row["payload"]) if row else None

    def list_runs(self, case_id: str) -> list[dict[str, Any]]:
        with self._transaction() as connection:
            rows = connection.execute(
                "SELECT payload FROM runs WHERE case_id = ? ORDER BY rowid",
                (case_id,),
            ).fetchall()
        return [json.loads(row["payload"]) for row in rows]

    def append_event(self, run_id: str, event_type: str, payload: dict[str, Any]) -> dict[str, Any]:
        occurred_at = datetime.now(UTC).isoformat()
        with self._transaction() as connection:
            cursor = connection.execute(
                "INSERT INTO events(run_id, event_type, payload, occurred_at) VALUES (?, ?, ?, ?)",
                (run_id, event_type, json.dumps(payload), occurred_at),
            )
            sequence = cursor.lastrowid
        return {"seq": sequence, "run_id": run_id, "event_type": event_type, "payload": payload, "occurred_at": occurred_at}

    def append_event_owned(self, run_id: str, lease_id: str, event_type: str, payload: dict[str, Any]) -> bool:
        occurred_at = datetime.now(UTC).isoformat()
        now = time.time()
        with self._transaction() as connection:
            cursor = connection.execute(
                """INSERT INTO events(run_id, event_type, payload, occurred_at)
                SELECT ?, ?, ?, ?
                WHERE EXISTS (
                    SELECT 1 FROM run_leases
                    WHERE run_id = ? AND lease_id = ? AND expires_at > ?
                )""",
                (run_id, event_type, json.dumps(payload), occurred_at, run_id, lease_id, now),
            )
        return cursor.rowcount == 1

    def events(self, run_id: str) -> list[dict[str, Any]]:
        with self._transaction() as connection:
            rows = connection.execute(
                "SELECT seq, run_id, event_type, payload, occurred_at FROM events WHERE run_id = ? ORDER BY seq",
                (run_id,),
            ).fetchall()
        return [
            {"seq": row["seq"], "run_id": row["run_id"], "event_type": row["event_type"], "payload": json.loads(row["payload"]), "occurred_at": row["occurred_at"]}
            for row in rows
        ]

    def save_checkpoint(self, run_id: str, payload: dict[str, Any]) -> str:
        checkpoint_id = f"checkpoint-{uuid4().hex}"
        created_at = datetime.now(UTC).isoformat()
        with self._transaction() as connection:
            connection.execute(
                "INSERT INTO checkpoints(id, run_id, payload, created_at) VALUES (?, ?, ?, ?)",
                (checkpoint_id, run_id, json.dumps(payload), created_at),
            )
        return checkpoint_id

    def save_checkpoint_owned(self, run_id: str, lease_id: str, payload: dict[str, Any]) -> str | None:
        checkpoint_id = f"checkpoint-{uuid4().hex}"
        created_at = datetime.now(UTC).isoformat()
        now = time.time()
        with self._transaction() as connection:
            cursor = connection.execute(
                """INSERT INTO checkpoints(id, run_id, payload, created_at)
                SELECT ?, ?, ?, ?
                WHERE EXISTS (
                    SELECT 1 FROM run_leases
                    WHERE run_id = ? AND lease_id = ? AND expires_at > ?
                )""",
                (checkpoint_id, run_id, json.dumps(payload), created_at, run_id, lease_id, now),
            )
        return checkpoint_id if cursor.rowcount == 1 else None

    def latest_checkpoint(self, run_id: str) -> dict[str, Any] | None:
        with self._transaction() as connection:
            row = connection.execute(
                "SELECT id, run_id, payload, created_at FROM checkpoints WHERE run_id = ? ORDER BY created_at DESC, rowid DESC LIMIT 1",
                (run_id,),
            ).fetchone()
        return {"id": row["id"], "run_id": row["run_id"], "payload": json.loads(row["payload"]), "created_at": row["created_at"]} if row else None

    def save_memory(self, payload: dict[str, Any]) -> None:
        with self._transaction() as connection:
            connection.execute(
                """INSERT INTO investment_memory(target, payload, updated_at) VALUES (?, ?, ?)
                ON CONFLICT(target) DO UPDATE SET payload=excluded.payload, updated_at=excluded.updated_at""",
                (payload["target"], json.dumps(payload), payload["updated_at"]),
            )

    def get_memory(self, target: str) -> dict[str, Any] | None:
        with self._transaction() as connection:
            row = connection.execute("SELECT payload FROM investment_memory WHERE target = ?", (target,)).fetchone()
        return json.loads(row["payload"]) if row else None
