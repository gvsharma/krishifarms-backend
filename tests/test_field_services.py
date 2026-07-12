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
