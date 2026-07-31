"""Analytics Hub API routes."""

from datetime import date
from uuid import UUID

from fastapi import APIRouter, Depends, Query
from fastapi.responses import Response
from sqlalchemy.orm import Session

from app.core.dependencies import CurrentUserContext, get_db, require_permission
from app.modules.analytics import service
from app.modules.analytics.export import export_module_csv
from app.modules.analytics.schemas import (
    AnalyticsCatalogResponse,
    AnalyticsFilter,
    ExportRequest,
    ModuleSummaryResponse,
    SeriesResponse,
    TablesResponse,
)
from app.shared.schemas.common import APIResponse

router = APIRouter(tags=["Analytics"])


def _filters_from_query(
    date_from: date | None = None,
    date_to: date | None = None,
    village_id: UUID | None = None,
    crop_type_id: UUID | None = None,
    farmer_id: UUID | None = None,
    buyer_id: UUID | None = None,
    asset_id: UUID | None = None,
    season: str | None = None,
    preset: str | None = None,
) -> AnalyticsFilter:
    return AnalyticsFilter(
        date_from=date_from,
        date_to=date_to,
        village_id=village_id,
        crop_type_id=crop_type_id,
        farmer_id=farmer_id,
        buyer_id=buyer_id,
        asset_id=asset_id,
        season=season,
        preset=preset,
    )


@router.get("/analytics/catalog", response_model=APIResponse[AnalyticsCatalogResponse])
def analytics_catalog(
    ctx: CurrentUserContext = Depends(require_permission("analytics:admin")),
):
    _ = ctx
    return APIResponse(data=service.get_catalog())


@router.get(
    "/analytics/{module}/summary",
    response_model=APIResponse[ModuleSummaryResponse],
)
def analytics_module_summary(
    module: str,
    date_from: date | None = Query(None),
    date_to: date | None = Query(None),
    village_id: UUID | None = Query(None),
    crop_type_id: UUID | None = Query(None),
    farmer_id: UUID | None = Query(None),
    buyer_id: UUID | None = Query(None),
    asset_id: UUID | None = Query(None),
    season: str | None = Query(None),
    preset: str | None = Query(None),
    ctx: CurrentUserContext = Depends(require_permission("analytics:admin")),
    db: Session = Depends(get_db),
):
    filters = _filters_from_query(
        date_from, date_to, village_id, crop_type_id, farmer_id, buyer_id, asset_id, season, preset
    )
    summary = service.get_module_summary(db, ctx.user.org_id, module, filters)
    return APIResponse(data=summary)


@router.get(
    "/analytics/{module}/series",
    response_model=APIResponse[SeriesResponse],
)
def analytics_module_series(
    module: str,
    date_from: date | None = Query(None),
    date_to: date | None = Query(None),
    village_id: UUID | None = Query(None),
    crop_type_id: UUID | None = Query(None),
    farmer_id: UUID | None = Query(None),
    buyer_id: UUID | None = Query(None),
    asset_id: UUID | None = Query(None),
    season: str | None = Query(None),
    preset: str | None = Query(None),
    ctx: CurrentUserContext = Depends(require_permission("analytics:admin")),
    db: Session = Depends(get_db),
):
    filters = _filters_from_query(
        date_from, date_to, village_id, crop_type_id, farmer_id, buyer_id, asset_id, season, preset
    )
    data = service.get_module_series(db, ctx.user.org_id, module, filters)
    return APIResponse(data=data)


@router.get(
    "/analytics/{module}/tables",
    response_model=APIResponse[TablesResponse],
)
def analytics_module_tables(
    module: str,
    date_from: date | None = Query(None),
    date_to: date | None = Query(None),
    village_id: UUID | None = Query(None),
    crop_type_id: UUID | None = Query(None),
    farmer_id: UUID | None = Query(None),
    buyer_id: UUID | None = Query(None),
    asset_id: UUID | None = Query(None),
    season: str | None = Query(None),
    preset: str | None = Query(None),
    ctx: CurrentUserContext = Depends(require_permission("analytics:admin")),
    db: Session = Depends(get_db),
):
    filters = _filters_from_query(
        date_from, date_to, village_id, crop_type_id, farmer_id, buyer_id, asset_id, season, preset
    )
    data = service.get_module_tables(db, ctx.user.org_id, module, filters)
    return APIResponse(data=data)


@router.post("/analytics/export")
def analytics_export(
    body: ExportRequest,
    ctx: CurrentUserContext = Depends(require_permission("analytics:admin")),
    db: Session = Depends(get_db),
):
    filters = AnalyticsFilter(
        date_from=body.date_from,
        date_to=body.date_to,
        village_id=body.village_id,
        crop_type_id=body.crop_type_id,
        farmer_id=body.farmer_id,
        buyer_id=body.buyer_id,
        asset_id=body.asset_id,
        season=body.season,
        preset=body.preset,
    )
    exported = export_module_csv(db, ctx.user.org_id, body.module, filters)
    return Response(
        content=exported.content,
        media_type=exported.content_type,
        headers={
            "Content-Disposition": f'attachment; filename="{exported.filename}"',
            "X-Row-Count": str(exported.row_count),
        },
    )
