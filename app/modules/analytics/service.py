"""Analytics service orchestrator — cache, latency, module dispatch."""

from __future__ import annotations

import time
from datetime import date
from uuid import UUID

from sqlalchemy.orm import Session

from app.core.exceptions import AppError
from app.modules.analytics import cache as analytics_cache
from app.modules.analytics.catalog import get_catalog, get_module_meta
from app.modules.analytics.filters import resolve_date_range
from app.modules.analytics.schemas import (
    LIVE_MODULES,
    AnalyticsFilter,
    ModuleSummaryResponse,
    SeriesPoint,
    SeriesResponse,
    TablePage,
    TablesResponse,
)
from app.modules.analytics.service_executive import build_executive_summary
from app.modules.analytics.service_finance import build_finance_summary
from app.modules.analytics.service_operations import build_operations_summary
from app.modules.analytics.service_procurement import build_procurement_summary
from app.modules.analytics.service_scaffold import build_scaffold_summary_for_org


def _build_summary(
    db: Session,
    org_id: UUID,
    module: str,
    filters: AnalyticsFilter,
    *,
    today: date | None = None,
) -> ModuleSummaryResponse:
    if module == "executive":
        return build_executive_summary(db, org_id, filters, today=today)
    if module == "operations":
        return build_operations_summary(db, org_id, filters, today=today)
    if module == "procurement":
        return build_procurement_summary(db, org_id, filters, today=today)
    if module == "finance":
        return build_finance_summary(db, org_id, filters, today=today)
    meta = get_module_meta(module)
    if meta is None:
        raise AppError("Unknown analytics module", status_code=404, details={"module": module})
    return build_scaffold_summary_for_org(module, org_id, filters, today=today)


def get_module_summary(
    db: Session,
    org_id: UUID,
    module: str,
    filters: AnalyticsFilter,
    *,
    today: date | None = None,
) -> ModuleSummaryResponse:
    started = time.perf_counter()
    key = analytics_cache.cache_key(org_id, module, "summary", filters)
    cached = analytics_cache.get_json(key)
    if cached is not None:
        payload = ModuleSummaryResponse.model_validate(cached)
        payload.cache_hit = True
        latency_ms = int((time.perf_counter() - started) * 1000)
        payload.latency_ms = latency_ms
        analytics_cache.log_latency(module, latency_ms, cache_hit=True, org_id=org_id)
        return payload

    summary = _build_summary(db, org_id, module, filters, today=today)
    summary.cache_hit = False
    latency_ms = int((time.perf_counter() - started) * 1000)
    summary.latency_ms = latency_ms
    analytics_cache.set_json(key, summary.model_dump(mode="json"))
    analytics_cache.log_latency(module, latency_ms, cache_hit=False, org_id=org_id)
    return summary


def get_module_series(
    db: Session,
    org_id: UUID,
    module: str,
    filters: AnalyticsFilter,
    *,
    today: date | None = None,
) -> SeriesResponse:
    summary = get_module_summary(db, org_id, module, filters, today=today)
    points: list[SeriesPoint] = list(summary.series_preview)
    return SeriesResponse(
        module=module,
        id=f"{module}_primary",
        points=points,
        unit="INR" if module in LIVE_MODULES else None,
        cache_hit=summary.cache_hit,
    )


def get_module_tables(
    db: Session,
    org_id: UUID,
    module: str,
    filters: AnalyticsFilter,
    *,
    today: date | None = None,
) -> TablesResponse:
    summary = get_module_summary(db, org_id, module, filters, today=today)
    tables: list[TablePage] = list(summary.tables_preview)
    return TablesResponse(module=module, tables=tables, cache_hit=summary.cache_hit)


def resolved_filters(filters: AnalyticsFilter, *, today: date | None = None) -> AnalyticsFilter:
    date_from, date_to = resolve_date_range(filters, today=today)
    return filters.model_copy(update={"date_from": date_from, "date_to": date_to})


__all__ = [
    "get_catalog",
    "get_module_summary",
    "get_module_series",
    "get_module_tables",
    "resolved_filters",
]
