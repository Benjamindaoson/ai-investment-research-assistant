"""Redis dispatch adapter with database-event recovery semantics."""

from __future__ import annotations

from typing import Any, Protocol

from redis import Redis


class RunQueue(Protocol):
    def enqueue(self, run_id: str) -> None: ...

    def dequeue(self, timeout: int = 0) -> str | None: ...


class RedisRunQueue:
    def __init__(self, url: str, name: str = "deepresearch:runs") -> None:
        if not url.strip():
            raise ValueError("Redis URL must not be blank")
        self.name = name
        self.pending_name = f"{name}:pending"
        self.client: Redis = Redis.from_url(url, decode_responses=True)
        self.client.ping()

    def enqueue(self, run_id: str) -> None:
        if self.client.sadd(self.pending_name, run_id):
            self.client.rpush(self.name, run_id)

    def dequeue(self, timeout: int = 0) -> str | None:
        item: Any = self.client.blpop(self.name, timeout=timeout) if timeout else self.client.lpop(self.name)
        if item is None:
            return None
        run_id = item[1] if isinstance(item, tuple) else item
        self.client.srem(self.pending_name, run_id)
        return str(run_id)

    def close(self) -> None:
        self.client.close()
