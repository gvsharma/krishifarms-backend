"""Document management enhancements for bills, OCR, voice notes, and archival."""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "202506210007"
down_revision: Union[str, None] = "202506210006"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column("documents", sa.Column("locale", sa.String(length=10), nullable=True))
    op.add_column("documents", sa.Column("ocr_status", sa.String(length=20), nullable=True))
    op.add_column(
        "documents",
        sa.Column("is_archived", sa.Boolean(), server_default=sa.text("false"), nullable=False),
    )
    op.add_column("documents", sa.Column("archived_at", sa.DateTime(timezone=True), nullable=True))
    op.create_check_constraint(
        "ck_documents_file_size_bytes",
        "documents",
        "file_size_bytes > 0",
    )
    op.create_index(
        "uq_documents_org_s3_key",
        "documents",
        ["org_id", "s3_key"],
        unique=True,
    )
    op.create_index(
        "ix_documents_org_type_created",
        "documents",
        ["org_id", "document_type", "created_at"],
    )
    op.create_index(
        "ix_documents_metadata",
        "documents",
        ["metadata"],
        postgresql_using="gin",
        postgresql_ops={"metadata": "jsonb_path_ops"},
    )

    op.add_column("document_links", sa.Column("org_id", postgresql.UUID(as_uuid=True), nullable=True))
    op.add_column("document_links", sa.Column("created_by", postgresql.UUID(as_uuid=True), nullable=True))
    op.execute("UPDATE document_links dl SET org_id = d.org_id FROM documents d WHERE dl.document_id = d.id")
    op.alter_column("document_links", "org_id", nullable=False)
    op.create_foreign_key(
        "fk_document_links_org_id",
        "document_links",
        "organizations",
        ["org_id"],
        ["id"],
        ondelete="RESTRICT",
    )
    op.create_foreign_key(
        "fk_document_links_created_by",
        "document_links",
        "users",
        ["created_by"],
        ["id"],
        ondelete="SET NULL",
    )
    op.create_index(
        "uq_document_links_unique",
        "document_links",
        ["document_id", "entity_type", "entity_id", "link_role"],
        unique=True,
    )


def downgrade() -> None:
    op.drop_index("uq_document_links_unique", table_name="document_links")
    op.drop_constraint("fk_document_links_created_by", "document_links", type_="foreignkey")
    op.drop_constraint("fk_document_links_org_id", "document_links", type_="foreignkey")
    op.drop_column("document_links", "created_by")
    op.drop_column("document_links", "org_id")
    op.drop_index("ix_documents_metadata", table_name="documents")
    op.drop_index("ix_documents_org_type_created", table_name="documents")
    op.drop_index("uq_documents_org_s3_key", table_name="documents")
    op.drop_constraint("ck_documents_file_size_bytes", "documents", type_="check")
    op.drop_column("documents", "archived_at")
    op.drop_column("documents", "is_archived")
    op.drop_column("documents", "ocr_status")
    op.drop_column("documents", "locale")
