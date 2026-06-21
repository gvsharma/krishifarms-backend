from app.core.cache.base import CacheProvider


class RedisCacheProvider:
    """Redis-backed cache. Enable with CACHE_PROVIDER=redis and REDIS_URL."""

    def __init__(self, url: str) -> None:
        try:
            import redis
        except ImportError as exc:
            raise RuntimeError(
                "Redis cache selected but redis package is not installed. "
                "Install with: pip install 'krishifarms-backend[redis]'"
            ) from exc

        self._client = redis.from_url(url, decode_responses=True)

    def get(self, key: str) -> str | None:
        return self._client.get(key)

    def set(self, key: str, value: str, ttl_seconds: int | None = None) -> None:
        if ttl_seconds is None:
            self._client.set(key, value)
        else:
            self._client.setex(key, ttl_seconds, value)

    def delete(self, key: str) -> None:
        self._client.delete(key)

    def clear(self) -> None:
        self._client.flushdb()


def redis_cache_provider(url: str) -> CacheProvider:
    return RedisCacheProvider(url)
