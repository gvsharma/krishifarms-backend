"""Work → comment → diesel receipt flow (web + Android client edge cases)."""

from datetime import UTC, date, datetime
from decimal import Decimal
from unittest.mock import MagicMock, patch
from uuid import uuid4

import pytest

from app.core.client_context import ClientContext
from app.core.exceptions import AppError
from app.modules.auth.permission_catalog import COMMENT_CREATE, DOCUMENT_CREATE, ROLE_MOBILE_PERMISSIONS
from app.modules.documents.schemas import DocumentLinkRequest, PresignUploadRequest
from app.modules.documents.service import link_document, list_documents
from app.modules.financial.expense_service import sync_field_service_diesel_expense
from app.modules.financial.schemas import FIELD_SERVICE_SOURCE
from app.modules.platform.schemas import CommentCreateRequest
from app.modules.platform.service import create_comment
from app.shared.permissions import ROLE_PERMISSIONS


def _web_client() -> ClientContext:
    return ClientContext(device_id="web-browser-1", client_type="web", request_id="req-web-1")


def _android_client() -> ClientContext:
    return ClientContext(device_id="android-pixel-7", client_type="android", request_id="req-and-1")


class TestFieldOpsRoleMatrix:
    """RBAC required for web CRM and Android field apps."""

    def test_farmer_can_comment_on_field_work(self):
        farmer = set(ROLE_PERMISSIONS["FARMER"])
        assert "comments:read" in farmer
        assert "comments:create" in farmer
        assert "field_services:read" in farmer
        assert "field_services:create" not in farmer
        assert COMMENT_CREATE in ROLE_MOBILE_PERMISSIONS["FARMER"]

    def test_agent_and_driver_can_upload_diesel_receipts(self):
        for role in ("AGENT", "DRIVER"):
            perms = set(ROLE_PERMISSIONS[role])
            assert "documents:read" in perms
            assert "documents:create" in perms
            assert "field_services:create" in perms
            assert "comments:create" in perms
            mobile = ROLE_MOBILE_PERMISSIONS[role]
            assert DOCUMENT_CREATE in mobile

    def test_farmer_cannot_upload_documents(self):
        farmer = set(ROLE_PERMISSIONS["FARMER"])
        assert "documents:create" not in farmer


class TestFieldServiceDieselEdgeCases:
    def test_creates_expense_when_none_exists(self):
        db = MagicMock()
        org_id = uuid4()
        record_id = uuid4()
        actor = uuid4()
        created = MagicMock()
        with (
            patch(
                "app.modules.financial.expense_service.find_expense_by_source",
                return_value=None,
            ) as find,
            patch(
                "app.modules.financial.expense_service._fuel_category",
                return_value=MagicMock(id=uuid4()),
            ),
            patch(
                "app.modules.financial.expense_service._default_cash_payment_mode",
                return_value=MagicMock(id=uuid4()),
            ),
            patch(
                "app.modules.financial.expense_service.create_expense",
                return_value=created,
            ) as create,
        ):
            result = sync_field_service_diesel_expense(
                db,
                org_id,
                record_id=record_id,
                record_number="FSR-0100",
                service_date=date(2026, 7, 13),
                asset_id=None,
                diesel_amount=Decimal("350.555"),
                record_status="open",
                actor_user_id=actor,
            )
        assert result is created
        find.assert_called_once()
        assert find.call_args.kwargs.get("include_deleted") is True
        assert find.call_args.args[2] == FIELD_SERVICE_SOURCE
        create.assert_called_once()
        assert create.call_args.kwargs["source_type"] == FIELD_SERVICE_SOURCE
        assert create.call_args.kwargs["source_id"] == record_id
        assert create.call_args.kwargs["commit"] is False
        assert create.call_args.args[2].amount == Decimal("350.56")

    def test_reactivates_soft_deleted_expense_on_reopen(self):
        existing = MagicMock()
        existing.deleted_at = datetime.now(UTC)
        existing.status = "reversed"
        db = MagicMock()
        with patch(
            "app.modules.financial.expense_service.find_expense_by_source",
            return_value=existing,
        ):
            result = sync_field_service_diesel_expense(
                db,
                uuid4(),
                record_id=uuid4(),
                record_number="FSR-0101",
                service_date=date(2026, 7, 13),
                asset_id=uuid4(),
                diesel_amount=Decimal("100.00"),
                record_status="completed",
                actor_user_id=uuid4(),
            )
        assert result is existing
        assert existing.deleted_at is None
        assert existing.status == "posted"
        assert existing.amount == Decimal("100.00")

    def test_zero_diesel_does_not_touch_already_reversed(self):
        existing = MagicMock()
        existing.deleted_at = datetime.now(UTC)
        existing.status = "reversed"
        with patch(
            "app.modules.financial.expense_service.find_expense_by_source",
            return_value=existing,
        ):
            result = sync_field_service_diesel_expense(
                MagicMock(),
                uuid4(),
                record_id=uuid4(),
                record_number="FSR-0102",
                service_date=date(2026, 7, 13),
                asset_id=None,
                diesel_amount=Decimal("0"),
                record_status="open",
                actor_user_id=uuid4(),
            )
        assert result is None
        # Already reversed — leave timestamps alone
        assert existing.status == "reversed"

    def test_cancelled_reverses_active_expense(self):
        existing = MagicMock()
        existing.deleted_at = None
        existing.status = "posted"
        with patch(
            "app.modules.financial.expense_service.find_expense_by_source",
            return_value=existing,
        ):
            result = sync_field_service_diesel_expense(
                MagicMock(),
                uuid4(),
                record_id=uuid4(),
                record_number="FSR-0103",
                service_date=date(2026, 7, 13),
                asset_id=None,
                diesel_amount=Decimal("200.00"),
                record_status="cancelled",
                actor_user_id=uuid4(),
            )
        assert result is None
        assert existing.status == "reversed"
        assert existing.deleted_at is not None

    def test_schema_rejects_negative_diesel(self):
        from app.modules.field_services.schemas import FieldServiceRecordCreateRequest

        with pytest.raises(Exception):
            FieldServiceRecordCreateRequest(
                service_category="tractor_work",
                service_date=date(2026, 7, 13),
                diesel_amount=Decimal("-1.00"),
            )


class TestFieldServiceCommentsWebAndAndroid:
    def test_android_comment_stores_client_type_and_skips_farmer_push(self):
        db = MagicMock()
        org_id = uuid4()
        entity_id = uuid4()
        author = uuid4()
        payload = CommentCreateRequest(
            entity_type="field_service",
            entity_id=entity_id,
            body="Looks good — please attach diesel bill",
            body_te=None,
        )
        with patch("app.modules.platform.service._audit"):
            row = create_comment(db, org_id, payload, author, _android_client())
        assert row.entity_type == "field_service"
        assert row.entity_id == entity_id
        assert row.client_type == "android"
        assert row.device_id == "android-pixel-7"
        assert row.author_user_id == author
        db.add.assert_called_once()
        db.commit.assert_called_once()
        # field_service comments must not import/call farmer push
        assert not hasattr(row, "_notify_called")

    def test_web_comment_stores_web_client_type(self):
        db = MagicMock()
        payload = CommentCreateRequest(
            entity_type="field_service",
            entity_id=uuid4(),
            body="Farmer acknowledged work",
        )
        with patch("app.modules.platform.service._audit"):
            row = create_comment(db, uuid4(), payload, uuid4(), _web_client())
        assert row.client_type == "web"
        assert row.device_id == "web-browser-1"

    def test_farmer_entity_still_attempts_push(self):
        db = MagicMock()
        farmer_id = uuid4()
        payload = CommentCreateRequest(
            entity_type="farmer",
            entity_id=farmer_id,
            body="Call me tomorrow",
        )
        with (
            patch("app.modules.platform.service._audit"),
            patch("app.modules.devices.service.notify_farmer_comment") as notify,
        ):
            create_comment(db, uuid4(), payload, uuid4(), _android_client())
        notify.assert_called_once()


class TestDieselReceiptDocuments:
    def test_list_documents_joins_for_field_service(self):
        db = MagicMock()
        query = MagicMock()
        query.filter.return_value = query
        query.join.return_value = query
        query.distinct.return_value = query
        query.order_by.return_value = query
        query.count.return_value = 0
        query.offset.return_value = query
        query.limit.return_value = query
        query.all.return_value = []
        db.query.return_value = query

        list_documents(
            db,
            uuid4(),
            1,
            20,
            entity_type="field_service",
            entity_id=uuid4(),
        )
        query.join.assert_called_once()

    def test_link_fuel_bill_to_field_service_web_and_android(self):
        for client in (_web_client(), _android_client()):
            db = MagicMock()
            doc = MagicMock()
            doc.id = uuid4()
            payload = DocumentLinkRequest(
                entity_type="field_service",
                entity_id=uuid4(),
                link_role="primary_attachment",
            )
            with (
                patch("app.modules.documents.service.get_document", return_value=doc),
                patch("app.modules.documents.service.write_audit_log") as audit,
            ):
                link = link_document(db, uuid4(), doc.id, payload, uuid4(), client=client)
            assert link.entity_type == "field_service"
            assert link.document_id == doc.id
            audit.assert_called_once()
            assert audit.call_args.kwargs["client_type"] == client.client_type
            assert audit.call_args.kwargs["device_id"] == client.device_id

    def test_presign_accepts_fuel_bill_type(self):
        req = PresignUploadRequest(
            document_type="fuel_bill",
            file_name="diesel-receipt.jpg",
            mime_type="image/jpeg",
            file_size_bytes=1024,
        )
        assert req.document_type == "fuel_bill"

    def test_list_documents_rejects_partial_entity_filter(self):
        with pytest.raises(AppError, match="together"):
            list_documents(MagicMock(), uuid4(), 1, 20, entity_type="field_service", entity_id=None)
