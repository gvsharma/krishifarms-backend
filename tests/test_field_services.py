"""Field services API tests."""

from decimal import Decimal

from app.modules.field_services.models import SERVICE_CATEGORIES
from app.shared.permissions import ROLE_PERMISSIONS


def test_service_categories_cover_user_requirements():
    required = {
        "field_service",
        "tractor_work",
        "transport",
        "fertiliser",
        "seeds",
        "agri_finance",
        "vehicle_ops",
        "godown",
    }
    assert required == SERVICE_CATEGORIES


def test_manager_has_field_services_crud_except_delete():
    perms = set(ROLE_PERMISSIONS["MANAGER"])
    assert "field_services:read" in perms
    assert "field_services:create" in perms
    assert "field_services:update" in perms
    assert "field_services:delete" not in perms


def test_agent_can_create_field_services():
    perms = set(ROLE_PERMISSIONS["AGENT"])
    assert "field_services:create" in perms
    assert "field_services:update" in perms


def test_money_defaults_are_decimal_compatible():
    from app.modules.field_services.schemas import FieldServiceRecordCreateRequest
    from datetime import date

    payload = FieldServiceRecordCreateRequest(
        service_category="agri_finance",
        service_date=date(2026, 7, 12),
        amount_given=Decimal("10000.00"),
        pending_amount=Decimal("5000.00"),
        total_amount=Decimal("15000.00"),
    )
    assert payload.pending_amount == Decimal("5000.00")


def test_field_service_response_includes_diesel_expense_id():
    from app.modules.field_services.schemas import FieldServiceRecordResponse
    from datetime import date, datetime, timezone
    from uuid import uuid4

    expense_id = uuid4()
    row = FieldServiceRecordResponse(
        id=uuid4(),
        record_number="FSR-0001",
        service_category="tractor_work",
        activity_type_id=None,
        farmer_id=None,
        asset_id=None,
        vehicle_type_id=None,
        service_date=date(2026, 7, 12),
        location=None,
        location_te=None,
        hours=None,
        bag_count=None,
        quantity=None,
        quantity_unit=None,
        rate_per_unit=None,
        diesel_amount=Decimal("100.00"),
        amount_given=Decimal("0"),
        advance_amount=Decimal("0"),
        total_amount=Decimal("0"),
        pending_amount=Decimal("0"),
        cleaning_status=None,
        facility_status=None,
        status="open",
        comments=None,
        comments_te=None,
        diesel_expense_id=expense_id,
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc),
    )
    assert row.diesel_expense_id == expense_id
