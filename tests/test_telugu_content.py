"""Tests for Telugu bilingual content (`*_te` fields) exposed via API schemas."""

from app.modules.financial.schemas import ExpenseCategoryCreateRequest, ExpenseCategoryResponse
from app.modules.legal import service as legal_service
from app.modules.master_data.schemas import CropTypeCreateRequest, VillageCreateRequest
from app.modules.users.schemas import RoleResponse, UserSelfUpdateRequest


def test_village_schema_accepts_name_te():
    payload = VillageCreateRequest(name="Bhairkhanpally", name_te="భైర్ఖాన్‌పల్లి")
    assert payload.name_te == "భైర్ఖాన్‌పల్లి"


def test_crop_type_schema_accepts_name_te():
    payload = CropTypeCreateRequest(name="Paddy", name_te="వరి", code="PADDY")
    assert payload.name_te == "వరి"


def test_expense_category_schema_accepts_name_te():
    payload = ExpenseCategoryCreateRequest(name="Fuel", name_te="ఇంధనం")
    assert payload.name_te == "ఇంధనం"


def test_role_response_includes_name_te():
    role = RoleResponse.model_validate(
        {
            "id": "00000000-0000-4000-8000-000000000001",
            "code": "MANAGER",
            "name": "Manager",
            "name_te": "నిర్వాహకుడు",
        }
    )
    assert role.name_te == "నిర్వాహకుడు"


def test_expense_category_response_includes_name_te():
    row = ExpenseCategoryResponse.model_validate(
        {
            "id": "00000000-0000-4000-8000-000000000002",
            "org_id": "00000000-0000-4000-8000-000000000003",
            "name": "Fuel",
            "name_te": "ఇంధనం",
            "parent_id": None,
            "type": "expense",
            "created_at": "2026-01-01T00:00:00Z",
            "updated_at": "2026-01-01T00:00:00Z",
        }
    )
    assert row.name_te == "ఇంధనం"


def test_user_self_update_accepts_full_name_te():
    payload = UserSelfUpdateRequest(full_name_te="రాజేష్")
    assert payload.full_name_te == "రాజేష్"


def test_legal_privacy_includes_telugu_content():
    privacy = legal_service.privacy_policy()
    assert privacy.title_te
    assert privacy.summary_te
    assert "కృషీఫార్మ్స్" in privacy.title_te


def test_legal_account_deletion_includes_telugu_content():
    info = legal_service.account_deletion_info()
    assert info.title_te
    assert info.instructions_te
    assert "ఖాతా" in info.title_te
