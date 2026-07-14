"""Scaffold module responses — honest empty states, no fake KPIs."""

from __future__ import annotations

from datetime import date
from uuid import UUID

from app.modules.analytics.catalog import get_module_meta
from app.modules.analytics.filters import resolve_date_range
from app.modules.analytics.schemas import (
    AnalyticsFilter,
    DataAvailabilityItem,
    KpiCard,
    ModuleSummaryResponse,
)


def build_scaffold_summary(
    module: str,
    filters: AnalyticsFilter,
    *,
    today: date | None = None,
) -> ModuleSummaryResponse:
    today = today or date.today()
    date_from, date_to = resolve_date_range(filters, today=today)
    meta = get_module_meta(module)
    missing = list(meta.missing_sources) if meta else ["Module not fully defined"]

    availability = [
        DataAvailabilityItem(source=src, status="missing", notes=src) for src in missing
    ]
    if not availability:
        availability = [
            DataAvailabilityItem(
                source="phase2",
                status="missing",
                notes="Planned for a later phase — no fabricated figures.",
            )
        ]

    return ModuleSummaryResponse(
        module=module,
        status="scaffold",
        filters=AnalyticsFilter(
            date_from=date_from,
            date_to=date_to,
            village_id=filters.village_id,
            crop_type_id=filters.crop_type_id,
            farmer_id=filters.farmer_id,
            buyer_id=filters.buyer_id,
            asset_id=filters.asset_id,
            season=filters.season,
            preset=filters.preset,
        ),
        kpis=[
            KpiCard(
                id="coming_soon",
                label="Coming soon",
                label_te="త్వరలో",
                value=None,
                format="text",
                status="coming_soon",
                note="This module is scaffolded in Phase 1. Live KPIs ship when data sources exist.",
            )
        ],
        series_preview=[],
        tables_preview=[],
        data_availability=availability,
    )


# org_id accepted for signature parity with live builders (unused — no queries).
def build_scaffold_summary_for_org(
    module: str,
    org_id: UUID,
    filters: AnalyticsFilter,
    *,
    today: date | None = None,
) -> ModuleSummaryResponse:
    _ = org_id
    return build_scaffold_summary(module, filters, today=today)
