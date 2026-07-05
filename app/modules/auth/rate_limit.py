"""Simple rate limiting for auth endpoints using the configured cache provider."""

from app.core.cache import get_cache_provider
from app.core.config import settings
from app.core.exceptions import AppError


def check_firebase_login_rate_limit(client_key: str) -> None:
    """Limit Firebase login attempts per IP (or key) per minute."""
    limit = settings.firebase_login_rate_limit_per_minute
    if limit <= 0:
        return

    cache = get_cache_provider()
    cache_key = f"auth:firebase-login:{client_key}"
    raw = cache.get(cache_key)
    count = int(raw) if raw is not None else 0
    if count >= limit:
        raise AppError("Too many login attempts. Try again later.", status_code=429)

    cache.set(cache_key, str(count + 1), ttl_seconds=60)
