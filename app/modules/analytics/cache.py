"""Redis/memory cache helpers for analytics payloads."""

from __future__ import annotations

import hashlib
import json
import logging
from typing import Any
from uuid import UUID

from app.core.cache import get_cache_provider
from app.core.config import settings
from app.modules.analytics.schemas import AnalyticsFilter

logger = logging.getLogger(__name__)

# Phase 1 cache window: 60–300s (config default 300)
ANALYTICS_CACHE_TTL_MIN = 60
ANALYTICS_CACHE_TTL_MAX = 300


def filter_hash(filters: AnalyticsFilter) -> str:
    payload = filters.model_dump(mode="json", exclude_none=True)
    raw = json.dumps(payload, sort_keys=True, default=str)
    return hashlib.sha256(raw.encode()).hexdigest()[:16]


def cache_key(org_id: UUID, module: str, kind: str, filters: AnalyticsFilter) -> str:
    return f"analytics:{org_id}:{module}:{kind}:{filter_hash(filters)}"


def ttl_seconds() -> int:
    configured = int(getattr(settings, "cache_ttl_seconds", 300) or 300)
    return max(ANALYTICS_CACHE_TTL_MIN, min(ANALYTICS_CACHE_TTL_MAX, configured))


def get_json(key: str) -> dict[str, Any] | None:
    cache = get_cache_provider()
    raw = cache.get(key)
    if raw is None:
        return None
    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        logger.warning("analytics.cache.corrupt key=%s", key)
        return None


def set_json(key: str, payload: dict[str, Any]) -> None:
    cache = get_cache_provider()
    cache.set(key, json.dumps(payload, default=str), ttl_seconds=ttl_seconds())


def log_latency(module: str, latency_ms: int, *, cache_hit: bool, org_id: UUID) -> None:
    logger.info(
        "analytics.module.latency_ms module=%s org_id=%s latency_ms=%s cache_hit=%s",
        module,
        org_id,
        latency_ms,
        cache_hit,
    )
