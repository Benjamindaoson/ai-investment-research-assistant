"""PostgreSQL adapter for the runtime's JSON-domain persistence contract."""

from __future__ import annotations

import json
import time
from contextlib import contextmanager
from datetime import UTC, datetime
from typing import Any, cast
from urllib.parse import unquote, urlparse
from uuid import uuid4

import pg8000.dbapi  # type: ignore[import-untyped]

from deepresearch.persistence.store import SQLiteStore


def _payload(value: Any) -> dict[str, Any]:
    decoded = json.loads(value) if isinstance(value, str) else value
    if not isinstance(decoded, dict):
        raise TypeError("PostgreSQL JSON payload must be an object")
    return cast(dict[str, Any], decoded)


class _CursorAdapter:
    def __init__(self, cursor: Any) -> None:
        self.cursor = cursor

    @property
    def rowcount(self) -> int:
        return int(self.cursor.rowcount)

    def _row(self, value: Any) -> dict[str, Any] | None:
        if value is None:
            return None
        names = [column[0] for column in self.cursor.description]
        return dict(zip(names, value, strict=True))

    def fetchone(self) -> dict[str, Any] | None:
        return self._row(self.cursor.fetchone())

    def fetchall(self) -> list[dict[str, Any]]:
        rows: list[dict[str, Any]] = []
        for value in self.cursor.fetchall():
            row = self._row(value)
            if row is not None:
                rows.append(row)
        return rows


class _ConnectionAdapter:
    def __init__(self, connection: Any) -> None:
        self.connection = connection

    def execute(self, query: str, params: tuple[Any, ...] = ()) -> _CursorAdapter:
        cursor = self.connection.cursor()
        cursor.execute(query, params)
        return _CursorAdapter(cursor)


class PostgresStore(SQLiteStore):
    """Use PostgreSQL without changing the engine-facing store contract."""

    def __init__(self, dsn: str) -> None:
        if not dsn.strip():
            raise ValueError("PostgreSQL DSN must not be blank")
        self.dsn = dsn
        self._initialize()

    @contextmanager
    def _transaction(self):  # type: ignore[no-untyped-def]
        parsed = urlparse(self.dsn)
        if parsed.scheme not in {"postgres", "postgresql"} or not parsed.hostname:
            raise ValueError("PostgreSQL DSN must use postgresql:// or postgres://")
        connection = pg8000.dbapi.connect(
            user=unquote(parsed.username or ""),
            password=unquote(parsed.password or ""),
            host=parsed.hostname,
            port=parsed.port or 5432,
            database=parsed.path.lstrip("/") or None,
        )
        try:
            yield _ConnectionAdapter(connection)
            connection.commit()
        except Exception:
            connection.rollback()
            raise
        finally:
            connection.close()

    def _initialize(self) -> None:
        with self._transaction() as connection:
            schema = """
                CREATE TABLE IF NOT EXISTS cases (id TEXT PRIMARY KEY, payload JSONB NOT NULL);
                CREATE TABLE IF NOT EXISTS runs (id TEXT PRIMARY KEY, case_id TEXT NOT NULL, payload JSONB NOT NULL);
                CREATE TABLE IF NOT EXISTS events (
                    seq BIGSERIAL PRIMARY KEY,
                    run_id TEXT NOT NULL,
                    event_type TEXT NOT NULL,
                    payload JSONB NOT NULL,
                    occurred_at TIMESTAMPTZ NOT NULL
                );
                CREATE INDEX IF NOT EXISTS events_run_id_seq_idx ON events(run_id, seq);
                CREATE TABLE IF NOT EXISTS checkpoints (
                    id TEXT PRIMARY KEY,
                    run_id TEXT NOT NULL,
                    payload JSONB NOT NULL,
                    created_at TIMESTAMPTZ NOT NULL
                );
                CREATE INDEX IF NOT EXISTS checkpoints_run_id_created_idx ON checkpoints(run_id, created_at);
                CREATE TABLE IF NOT EXISTS run_leases (
                    run_id TEXT PRIMARY KEY,
                    lease_id TEXT NOT NULL,
                    acquired_at TIMESTAMPTZ NOT NULL,
                    expires_at DOUBLE PRECISION NOT NULL
                );
                CREATE TABLE IF NOT EXISTS evaluations (
                    id TEXT PRIMARY KEY,
                    run_id TEXT NOT NULL,
                    payload JSONB NOT NULL,
                    created_at TIMESTAMPTZ NOT NULL
                );
                CREATE INDEX IF NOT EXISTS evaluations_run_id_created_idx ON evaluations(run_id, created_at);
                CREATE TABLE IF NOT EXISTS investment_memory (
                    target TEXT PRIMARY KEY,
                    payload JSONB NOT NULL,
                    updated_at TIMESTAMPTZ NOT NULL
                );
                """
            for statement in schema.split(";"):
                if statement.strip():
                    connection.execute(statement)

    def acquire_run_lease(self, run_id: str, lease_id: str, ttl_seconds: float) -> bool:
        if ttl_seconds <= 0:
            raise ValueError("ttl_seconds must be positive")
        now = time.time()
        with self._transaction() as connection:
            connection.execute("DELETE FROM run_leases WHERE expires_at <= %s", (now,))
            cursor = connection.execute(
                """
                INSERT INTO run_leases(run_id, lease_id, acquired_at, expires_at)
                VALUES (%s, %s, %s, %s)
                ON CONFLICT (run_id) DO NOTHING
                """,
                (run_id, lease_id, datetime.now(UTC), now + ttl_seconds),
            )
        return bool(cursor.rowcount == 1)

    def release_run_lease(self, run_id: str, lease_id: str) -> bool:
        with self._transaction() as connection:
            cursor = connection.execute(
                "DELETE FROM run_leases WHERE run_id = %s AND lease_id = %s",
                (run_id, lease_id),
            )
        return bool(cursor.rowcount == 1)

    def renew_run_lease(self, run_id: str, lease_id: str, ttl_seconds: float) -> bool:
        if ttl_seconds <= 0:
            raise ValueError("ttl_seconds must be positive")
        now = time.time()
        with self._transaction() as connection:
            cursor = connection.execute(
                """
                UPDATE run_leases SET expires_at = %s
                WHERE run_id = %s AND lease_id = %s AND expires_at > %s
                """,
                (now + ttl_seconds, run_id, lease_id, now),
            )
        return bool(cursor.rowcount == 1)

    def save_case(self, payload: dict[str, Any]) -> None:
        with self._transaction() as connection:
            connection.execute(
                """
                INSERT INTO cases(id, payload) VALUES (%s, %s::jsonb)
                ON CONFLICT(id) DO UPDATE SET payload = EXCLUDED.payload
                """,
                (payload["id"], json.dumps(payload)),
            )

    def get_case(self, case_id: str) -> dict[str, Any] | None:
        with self._transaction() as connection:
            row = connection.execute("SELECT payload FROM cases WHERE id = %s", (case_id,)).fetchone()
        return _payload(row["payload"]) if row else None

    def list_cases(self) -> list[dict[str, Any]]:
        with self._transaction() as connection:
            rows = connection.execute("SELECT payload FROM cases ORDER BY id").fetchall()
        return [_payload(row["payload"]) for row in rows]

    def save_run(self, payload: dict[str, Any]) -> None:
        with self._transaction() as connection:
            connection.execute(
                """
                INSERT INTO runs(id, case_id, payload) VALUES (%s, %s, %s::jsonb)
                ON CONFLICT(id) DO UPDATE SET case_id = EXCLUDED.case_id, payload = EXCLUDED.payload
                """,
                (payload["id"], payload["case_id"], json.dumps(payload)),
            )

    def save_run_owned(self, payload: dict[str, Any], lease_id: str) -> bool:
        now = time.time()
        with self._transaction() as connection:
            current = connection.execute(
                "SELECT payload FROM runs WHERE id = %s",
                (payload["id"],),
            ).fetchone()
            if current is not None:
                current_payload = _payload(current["payload"])
                if current_payload.get("state") == "CANCELLED" and payload.get("state") != "CANCELLED":
                    return False
            cursor = connection.execute(
                """
                UPDATE runs SET case_id = %s, payload = %s::jsonb
                WHERE id = %s AND EXISTS (
                    SELECT 1 FROM run_leases
                    WHERE run_id = %s AND lease_id = %s AND expires_at > %s
                )
                """,
                (payload["case_id"], json.dumps(payload), payload["id"], payload["id"], lease_id, now),
            )
        return bool(cursor.rowcount == 1)

    def get_run(self, run_id: str) -> dict[str, Any] | None:
        with self._transaction() as connection:
            row = connection.execute("SELECT payload FROM runs WHERE id = %s", (run_id,)).fetchone()
        return _payload(row["payload"]) if row else None

    def save_evaluation(self, payload: dict[str, Any]) -> None:
        with self._transaction() as connection:
            connection.execute(
                "INSERT INTO evaluations(id, run_id, payload, created_at) VALUES (%s, %s, %s::jsonb, %s)",
                (payload["id"], payload["run_id"], json.dumps(payload), datetime.now(UTC)),
            )

    def latest_evaluation(self, run_id: str) -> dict[str, Any] | None:
        with self._transaction() as connection:
            row = connection.execute(
                "SELECT payload FROM evaluations WHERE run_id = %s ORDER BY created_at DESC, id DESC LIMIT 1",
                (run_id,),
            ).fetchone()
        return _payload(row["payload"]) if row else None

    def evaluation_count(self, run_id: str) -> int:
        with self._transaction() as connection:
            row = connection.execute(
                "SELECT COUNT(*) AS count FROM evaluations WHERE run_id = %s", (run_id,)
            ).fetchone()
        return int(row["count"])

    def list_runs(self, case_id: str | None = None) -> list[dict[str, Any]]:
        with self._transaction() as connection:
            if case_id is None:
                rows = connection.execute("SELECT payload FROM runs ORDER BY id").fetchall()
            else:
                rows = connection.execute(
                    "SELECT payload FROM runs WHERE case_id = %s ORDER BY id", (case_id,)
                ).fetchall()
        return [_payload(row["payload"]) for row in rows]

    def append_event(self, run_id: str, event_type: str, payload: dict[str, Any]) -> dict[str, Any]:
        occurred_at = datetime.now(UTC)
        with self._transaction() as connection:
            row = connection.execute(
                """
                INSERT INTO events(run_id, event_type, payload, occurred_at)
                VALUES (%s, %s, %s::jsonb, %s) RETURNING seq
                """,
                (run_id, event_type, json.dumps(payload), occurred_at),
            ).fetchone()
        return {
            "seq": row["seq"],
            "run_id": run_id,
            "event_type": event_type,
            "payload": payload,
            "occurred_at": occurred_at.isoformat(),
        }

    def append_event_owned(self, run_id: str, lease_id: str, event_type: str, payload: dict[str, Any]) -> bool:
        now = time.time()
        occurred_at = datetime.now(UTC)
        with self._transaction() as connection:
            row = connection.execute(
                """
                INSERT INTO events(run_id, event_type, payload, occurred_at)
                SELECT %s, %s, %s::jsonb, %s
                WHERE EXISTS (
                    SELECT 1 FROM run_leases
                    WHERE run_id = %s AND lease_id = %s AND expires_at > %s
                ) RETURNING seq
                """,
                (run_id, event_type, json.dumps(payload), occurred_at, run_id, lease_id, now),
            ).fetchone()
        return row is not None

    def events(self, run_id: str) -> list[dict[str, Any]]:
        with self._transaction() as connection:
            rows = connection.execute(
                "SELECT seq, run_id, event_type, payload, occurred_at FROM events WHERE run_id = %s ORDER BY seq",
                (run_id,),
            ).fetchall()
        return [
            {
                "seq": row["seq"],
                "run_id": row["run_id"],
                "event_type": row["event_type"],
                "payload": _payload(row["payload"]),
                "occurred_at": row["occurred_at"].isoformat(),
            }
            for row in rows
        ]

    def save_checkpoint(self, run_id: str, payload: dict[str, Any]) -> str:
        checkpoint_id = f"checkpoint-{uuid4().hex}"
        created_at = datetime.now(UTC)
        with self._transaction() as connection:
            connection.execute(
                "INSERT INTO checkpoints(id, run_id, payload, created_at) VALUES (%s, %s, %s::jsonb, %s)",
                (checkpoint_id, run_id, json.dumps(payload), created_at),
            )
        return checkpoint_id

    def save_checkpoint_owned(self, run_id: str, lease_id: str, payload: dict[str, Any]) -> str | None:
        checkpoint_id = f"checkpoint-{uuid4().hex}"
        now = time.time()
        created_at = datetime.now(UTC)
        with self._transaction() as connection:
            row = connection.execute(
                """
                INSERT INTO checkpoints(id, run_id, payload, created_at)
                SELECT %s, %s, %s::jsonb, %s
                WHERE EXISTS (
                    SELECT 1 FROM run_leases
                    WHERE run_id = %s AND lease_id = %s AND expires_at > %s
                ) RETURNING id
                """,
                (checkpoint_id, run_id, json.dumps(payload), created_at, run_id, lease_id, now),
            ).fetchone()
        return row["id"] if row else None

    def latest_checkpoint(self, run_id: str) -> dict[str, Any] | None:
        with self._transaction() as connection:
            row = connection.execute(
                "SELECT id, run_id, payload, created_at FROM checkpoints WHERE run_id = %s ORDER BY created_at DESC, id DESC LIMIT 1",
                (run_id,),
            ).fetchone()
        if row is None:
            return None
        return {
            "id": row["id"],
            "run_id": row["run_id"],
            "payload": _payload(row["payload"]),
            "created_at": row["created_at"].isoformat(),
        }

    def save_memory(self, payload: dict[str, Any]) -> None:
        with self._transaction() as connection:
            connection.execute(
                """
                INSERT INTO investment_memory(target, payload, updated_at) VALUES (%s, %s::jsonb, %s)
                ON CONFLICT(target) DO UPDATE SET payload = EXCLUDED.payload, updated_at = EXCLUDED.updated_at
                """,
                (payload["target"], json.dumps(payload), payload["updated_at"]),
            )

    def save_memory_owned(self, payload: dict[str, Any], run_id: str, lease_id: str) -> bool:
        now = time.time()
        with self._transaction() as connection:
            row = connection.execute(
                """
                INSERT INTO investment_memory(target, payload, updated_at)
                SELECT %s, %s::jsonb, %s
                WHERE EXISTS (
                    SELECT 1 FROM run_leases
                    WHERE run_id = %s AND lease_id = %s AND expires_at > %s
                )
                ON CONFLICT(target) DO UPDATE SET payload = EXCLUDED.payload, updated_at = EXCLUDED.updated_at
                RETURNING target
                """,
                (payload["target"], json.dumps(payload), payload["updated_at"], run_id, lease_id, now),
            ).fetchone()
        return row is not None

    def get_memory(self, target: str) -> dict[str, Any] | None:
        with self._transaction() as connection:
            row = connection.execute(
                "SELECT payload FROM investment_memory WHERE target = %s", (target,)
            ).fetchone()
        return _payload(row["payload"]) if row else None
