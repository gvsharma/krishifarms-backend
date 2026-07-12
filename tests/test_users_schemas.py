"""User schema accepts seeded *.local emails (EmailStr rejects reserved domains)."""

from datetime import UTC, datetime
from uuid import uuid4

import pytest
from pydantic import ValidationError

from app.modules.users.schemas import UserCreateRequest, UserResponse, UserUpdateRequest


def test_user_response_accepts_local_email():
    role_id = uuid4()
    now = datetime.now(UTC)
    user = UserResponse(
        id=uuid4(),
        org_id=uuid4(),
        email="owner@krishifarms.local",
        phone=None,
        full_name="Owner",
        preferred_locale="en",
        is_active=True,
        role={"id": role_id, "code": "OWNER", "name": "Owner"},
        last_login_at=None,
        created_at=now,
        updated_at=now,
    )
    assert user.email == "owner@krishifarms.local"


def test_user_create_accepts_local_email():
    payload = UserCreateRequest(
        email="manager@demo.krishifarms.local",
        password="DemoPass123!",
        full_name="Demo Manager",
        phone="9876543210",
        role_id=uuid4(),
    )
    assert payload.email == "manager@demo.krishifarms.local"
    assert payload.phone == "9876543210"


def test_user_create_requires_phone():
    with pytest.raises(ValidationError):
        UserCreateRequest(
            email="manager@demo.krishifarms.local",
            password="DemoPass123!",
            full_name="Demo Manager",
            role_id=uuid4(),
        )


def test_user_create_rejects_short_phone():
    with pytest.raises(ValidationError):
        UserCreateRequest(
            email="manager@demo.krishifarms.local",
            password="DemoPass123!",
            full_name="Demo Manager",
            phone="98765",
            role_id=uuid4(),
        )


def test_user_update_normalizes_phone():
    payload = UserUpdateRequest(phone="+91 98765 43210")
    assert payload.phone == "9876543210"


def test_user_update_rejects_clearing_phone():
    with pytest.raises(ValidationError):
        UserUpdateRequest(phone="")
