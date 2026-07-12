from datetime import date
from uuid import UUID

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.core.dependencies import CurrentUserContext, get_db, require_permission
from app.modules.assets import vehicle_trip_service as service
from app.modules.assets.vehicle_trip_schemas import (
    VehicleTripCreateRequest,
    VehicleTripListResponse,
    VehicleTripResponse,
    VehicleTripUpdateRequest,
)
from app.shared.schemas.common import APIResponse

router = APIRouter(tags=["Vehicles"])


def _trip_response(db, org_id: UUID, row) -> VehicleTripResponse:
    data = VehicleTripResponse.model_validate(row).model_dump()
    data["diesel_expense_id"] = service.diesel_expense_id_for_trip(db, org_id, row.id)
    return VehicleTripResponse.model_validate(data)


@router.get("/vehicle-trips", response_model=APIResponse[VehicleTripListResponse])
def list_vehicle_trips(
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
    asset_id: UUID | None = Query(default=None),
    driver_worker_id: UUID | None = Query(default=None),
    date_from: date | None = Query(default=None),
    date_to: date | None = Query(default=None),
    ctx: CurrentUserContext = Depends(require_permission("transport:read")),
    db: Session = Depends(get_db),
):
    items, total = service.list_trips(
        db,
        ctx.user.org_id,
        page=page,
        page_size=page_size,
        asset_id=asset_id,
        driver_worker_id=driver_worker_id,
        date_from=date_from,
        date_to=date_to,
    )
    return APIResponse(
        data=VehicleTripListResponse(
            items=[_trip_response(db, ctx.user.org_id, item) for item in items],
            total=total,
            page=page,
            page_size=page_size,
        )
    )


@router.post("/vehicle-trips", response_model=APIResponse[VehicleTripResponse], status_code=201)
def create_vehicle_trip(
    payload: VehicleTripCreateRequest,
    ctx: CurrentUserContext = Depends(require_permission("transport:create")),
    db: Session = Depends(get_db),
):
    row = service.create_trip(db, ctx.user.org_id, payload, ctx.user.id)
    return APIResponse(data=_trip_response(db, ctx.user.org_id, row))


@router.get("/vehicle-trips/{trip_id}", response_model=APIResponse[VehicleTripResponse])
def get_vehicle_trip(
    trip_id: UUID,
    trip_date: date = Query(...),
    ctx: CurrentUserContext = Depends(require_permission("transport:read")),
    db: Session = Depends(get_db),
):
    row = service.get_trip(db, ctx.user.org_id, trip_id, trip_date)
    return APIResponse(data=_trip_response(db, ctx.user.org_id, row))


@router.patch("/vehicle-trips/{trip_id}", response_model=APIResponse[VehicleTripResponse])
def update_vehicle_trip(
    trip_id: UUID,
    payload: VehicleTripUpdateRequest,
    trip_date: date = Query(...),
    ctx: CurrentUserContext = Depends(require_permission("transport:update")),
    db: Session = Depends(get_db),
):
    row = service.update_trip(db, ctx.user.org_id, trip_id, trip_date, payload, ctx.user.id)
    return APIResponse(data=_trip_response(db, ctx.user.org_id, row))
