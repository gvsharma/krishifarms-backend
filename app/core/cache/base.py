from typing import Protocol, runtime_checkable


@runtime_checkable
class CacheProvider(Protocol):
    """Cache abstraction. Swap implementation via CACHE_PROVIDER setting."""

    def get(self, key: str) -> str | None:
        """Return cached value or None if missing/expired."""

    def set(self, key: str, value: str, ttl_seconds: int | None = None) -> None:
        """Store a string value with optional TTL."""

    def delete(self, key: str) -> None:
        """Remove a single cache entry."""

    def clear(self) -> None:
        """Remove all entries managed by this provider."""
