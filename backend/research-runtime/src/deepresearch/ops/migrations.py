"""Minimal schema-version guard for runtime stores.

The runtime currently stores domain objects as JSON payloads, so migrations are
small operational checks rather than large ORM-managed schema rewrites. This
module records an explicit schema version in the backing store and lets
readiness fail loudly when the version table cannot be read or written.
"""

from __future__ import annotations

from typing import Any

SCHEMA_VERSION = "2026-10-09.1"


def _placeholder(store: object) -> str:
    return "%s" if type(store).__name__ == "PostgresStore" else "?"


def ensure_schema_version(store: object) -> dict[str, Any]:
    """Create/read the schema migration ledger and return its current status."""

    transaction = getattr(store, "_transaction", None)
    if transaction is None:
        raise RuntimeError("store does not expose a transaction boundary")

    placeholder = _placeholder(store)
    with transaction() as connection:
        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS schema_migrations (
                version TEXT PRIMARY KEY,
                applied_at TEXT NOT NULL
            )
            """
        )
        cursor = connection.execute(
            f"SELECT version, applied_at FROM schema_migrations WHERE version = {placeholder}",
            (SCHEMA_VERSION,),
        )
        current = cursor.fetchone()
        if current is None:
            connection.execute(
                f"INSERT INTO schema_migrations(version, applied_at) VALUES ({placeholder}, CURRENT_TIMESTAMP)",
                (SCHEMA_VERSION,),
            )
        rows = connection.execute("SELECT version, applied_at FROM schema_migrations ORDER BY applied_at").fetchall()

    versions = [str(row["version"]) for row in rows]
    return {
        "schema_version": SCHEMA_VERSION,
        "applied_versions": versions,
        "current": SCHEMA_VERSION in versions,
    }
