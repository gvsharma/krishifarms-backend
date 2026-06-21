from app.core.cache.base import CacheProvider


class NullCacheProvider:
    """No-op cache. Used when CACHE_PROVIDER=none."""

    def get(self, key: str) -> str | None:
        return None

    def set(self, key: str, value: str, ttl_seconds: int | None = None) -> None:
        return None

    def delete(self, key: str) -> None:
        return None

    def clear(self) -> None:
        return None


def null_cache_provider() -> CacheProvider:
    return NullCacheProvider()
