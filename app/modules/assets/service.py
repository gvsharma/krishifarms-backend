from datetime import UTC, datetime
from uuid import UUID
from re import sub

from sqlalchemy.orm import Session

from app.core.exceptions import ConflictError, NotFoundError
from app.modules.assets.models import Asset
from app.modules.assets.schemas import AssetCreateRequest, AssetUpdateRequest
from app.modules.platform.models import VehicleType
from app.shared.services.audit import write_audit_log


def _slug_code(name: str) -> str:
    cleaned = sub(r"[^A-Za-z0-9]+", "-", name.strip().upper()).strip("-")
    return (cleaned or "ASSET")[:40]


def _get_vehicle_type(db: Session, org_id: UUID, vehicle_type_id: UUID | None) -> VehicleType | None:
    if vehicle_type_id is None:
        return None
    row = (
        db.query(VehicleType)
        .filter(
            VehicleType.id == vehicle_type_id,
            VehicleType.org_id == org_id,
            VehicleType.deleted_at.is_(None),
        )
        .first()
    )
    if row is None:
        raise NotFoundError("Vehicle type not found")
    return row


def _enrich(asset: Asset, vehicle_type: VehicleType | None = None) -> dict:
    data = {
        "id": asset.id,
        "org_id": asset.org_id,
        "asset_code": asset.asset_code,
        "name": asset.name,
        "name_te": asset.name_te,
        "asset_category": asset.asset_category,
        "vehicle_type_id": asset.vehicle_type_id,
        "vehicle_type_name": vehicle_type.name if vehicle_type else None,
        "vehicle_type_code": vehicle_type.code if vehicle_type else None,
        "registration_number": asset.registration_number,
        "fuel_type": asset.fuel_type,
        "driver_name": asset.driver_name,
        "purchase_date": asset.purchase_date,
        "purchase_cost": asset.purchase_cost,
        "status": asset.status,
        "is_rentable": asset.is_rentable,
        "hourly_rate": asset.hourly_rate,
        "daily_rate": asset.daily_rate,
        "notes": asset.notes,
        "created_at": asset.created_at,
        "updated_at": asset.updated_at,
    }
    return data


def list_assets(
    db: Session,
    org_id: UUID,
    page: int,
    page_size: int,
    *,
    asset_category: str | None = None,
    status: str | None = None,
    vehicle_type_id: UUID | None = None,
) -> tuple[list[dict], int]:
    query = db.query(Asset).filter(Asset.org_id == org_id, Asset.deleted_at.is_(None))
    if asset_category:
        query = query.filter(Asset.asset_category == asset_category)
    if status:
        query = query.filter(Asset.status == status)
    if vehicle_type_id:
        query = query.filter(Asset.vehicle_type_id == vehicle_type_id)
    query = query.order_by(Asset.name)
    total = query.count()
    items = query.offset((page - 1) * page_size).limit(page_size).all()

    type_ids = {a.vehicle_type_id for a in items if a.vehicle_type_id}
    types_by_id: dict[UUID, VehicleType] = {}
    if type_ids:
        rows = (
            db.query(VehicleType)
            .filter(VehicleType.org_id == org_id, VehicleType.id.in_(type_ids))
            .all()
        )
        types_by_id = {row.id: row for row in rows}

    return [_enrich(a, types_by_id.get(a.vehicle_type_id) if a.vehicle_type_id else None) for a in items], total


def get_asset(db: Session, org_id: UUID, asset_id: UUID) -> dict:
    asset = (
        db.query(Asset)
        .filter(Asset.id == asset_id, Asset.org_id == org_id, Asset.deleted_at.is_(None))
        .first()
    )
    if asset is None:
        raise NotFoundError("Asset not found")
    vehicle_type = _get_vehicle_type(db, org_id, asset.vehicle_type_id)
    return _enrich(asset, vehicle_type)


def create_asset(
    db: Session, org_id: UUID, payload: AssetCreateRequest, actor_user_id: UUID
) -> dict:
    vehicle_type = _get_vehicle_type(db, org_id, payload.vehicle_type_id)
    asset_code = (payload.asset_code or _slug_code(payload.name)).strip().upper()

    existing = (
        db.query(Asset)
        .filter(Asset.org_id == org_id, Asset.asset_code == asset_code, Asset.deleted_at.is_(None))
        .first()
    )
    if existing:
        raise ConflictError("Asset code already exists")

    fuel_type = payload.fuel_type
    if fuel_type is None and vehicle_type is not None:
        fuel_type = vehicle_type.fuel_type

    data = payload.model_dump(exclude={"asset_code", "fuel_type"})
    asset = Asset(
        org_id=org_id,
        asset_code=asset_code,
        fuel_type=fuel_type,
        created_by=actor_user_id,
        updated_by=actor_user_id,
        **data,
    )
    db.add(asset)
    db.flush()
    write_audit_log(
        db,
        org_id=org_id,
        actor_user_id=actor_user_id,
        action="CREATE",
        entity_type="asset",
        entity_id=asset.id,
        after_state=payload.model_dump(mode="json"),
    )
    db.commit()
    db.refresh(asset)
    return _enrich(asset, vehicle_type)


def update_asset(
    db: Session,
    org_id: UUID,
    asset_id: UUID,
    payload: AssetUpdateRequest,
    actor_user_id: UUID,
) -> dict:
    asset = (
        db.query(Asset)
        .filter(Asset.id == asset_id, Asset.org_id == org_id, Asset.deleted_at.is_(None))
        .first()
    )
    if asset is None:
        raise NotFoundError("Asset not found")

    updates = payload.model_dump(exclude_unset=True)
    if "vehicle_type_id" in updates:
        _get_vehicle_type(db, org_id, updates["vehicle_type_id"])
    if "asset_code" in updates and updates["asset_code"]:
        new_code = updates["asset_code"].strip().upper()
        conflict = (
            db.query(Asset)
            .filter(
                Asset.org_id == org_id,
                Asset.asset_code == new_code,
                Asset.id != asset_id,
                Asset.deleted_at.is_(None),
            )
            .first()
        )
        if conflict:
            raise ConflictError("Asset code already exists")
        updates["asset_code"] = new_code

    before = {
        "name": asset.name,
        "asset_code": asset.asset_code,
        "status": asset.status,
        "vehicle_type_id": str(asset.vehicle_type_id) if asset.vehicle_type_id else None,
    }
    for field, value in updates.items():
        setattr(asset, field, value)
    asset.updated_by = actor_user_id
    write_audit_log(
        db,
        org_id=org_id,
        actor_user_id=actor_user_id,
        action="UPDATE",
        entity_type="asset",
        entity_id=asset.id,
        before_state=before,
        after_state=payload.model_dump(exclude_unset=True, mode="json"),
    )
    db.commit()
    db.refresh(asset)
    vehicle_type = _get_vehicle_type(db, org_id, asset.vehicle_type_id)
    return _enrich(asset, vehicle_type)


def delete_asset(db: Session, org_id: UUID, asset_id: UUID, actor_user_id: UUID) -> None:
    asset = (
        db.query(Asset)
        .filter(Asset.id == asset_id, Asset.org_id == org_id, Asset.deleted_at.is_(None))
        .first()
    )
    if asset is None:
        raise NotFoundError("Asset not found")
    asset.deleted_at = datetime.now(UTC)
    asset.updated_by = actor_user_id
    write_audit_log(
        db,
        org_id=org_id,
        actor_user_id=actor_user_id,
        action="DELETE",
        entity_type="asset",
        entity_id=asset.id,
    )
    db.commit()
