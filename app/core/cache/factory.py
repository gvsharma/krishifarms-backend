from app.core.cache.base import CacheProvider
from app.core.cache.memory import memory_cache_provider
from app.core.cache.null import null_cache_provider
from app.core.cache.redis import redis_cache_provider
from app.core.config import Settings, settings

_cache_provider: CacheProvider | None = None


def build_cache_provider(app_settings: Settings | None = None) -> CacheProvider:
    config = app_settings or settings
    provider = config.cache_provider.lower()

    if provider == "none":
        return null_cache_provider()
    if provider == "memory":
        return memory_cache_provider()
    if provider == "redis":
        if not config.redis_url:
            raise RuntimeError("CACHE_PROVIDER=redis requires REDIS_URL to be set")
        return redis_cache_provider(config.redis_url)

    raise RuntimeError(
        f"Unsupported CACHE_PROVIDER '{config.cache_provider}'. "
        "Supported values: none, memory, redis"
    )


def get_cache_provider() -> CacheProvider:
    global _cache_provider
    if _cache_provider is None:
        _cache_provider = build_cache_provider()
    return _cache_provider


def reset_cache_provider() -> None:
    """Reset singleton. Useful for tests."""
    global _cache_provider
    _cache_provider = None
