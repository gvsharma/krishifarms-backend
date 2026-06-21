from dataclasses import dataclass
from datetime import UTC, datetime, timedelta
from threading import Lock

from app.core.cache.base import CacheProvider


@dataclass
class _CacheEntry:
    value: str
    expires_at: datetime | None


class InMemoryCacheProvider:
    """Process-local cache with TTL. Default for single-EC2 deployments."""

    def __init__(self) -> None:
        self._store: dict[str, _CacheEntry] = {}
        self._lock = Lock()

    def get(self, key: str) -> str | None:
        with self._lock:
            entry = self._store.get(key)
            if entry is None:
                return None
            if entry.expires_at is not None and entry.expires_at <= datetime.now(UTC):
                del self._store[key]
                return None
            return entry.value

    def set(self, key: str, value: str, ttl_seconds: int | None = None) -> None:
        expires_at = None
        if ttl_seconds is not None:
            expires_at = datetime.now(UTC) + timedelta(seconds=ttl_seconds)
        with self._lock:
            self._store[key] = _CacheEntry(value=value, expires_at=expires_at)

    def delete(self, key: str) -> None:
        with self._lock:
            self._store.pop(key, None)

    def clear(self) -> None:
        with self._lock:
            self._store.clear()


def memory_cache_provider() -> CacheProvider:
    return InMemoryCacheProvider()
