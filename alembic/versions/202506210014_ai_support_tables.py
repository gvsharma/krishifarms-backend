"""AI support tables: jobs, suggestions, summaries, OCR, voice, WhatsApp."""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "202506210014"
down_revision: Union[str, None] = "202506210013"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "whatsapp_messages",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("org_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("external_message_id", sa.String(length=200), nullable=False),
        sa.Column("direction", sa.String(length=10), nullable=False),
        sa.Column("from_phone", sa.String(length=20), nullable=False),
        sa.Column("to_phone", sa.String(length=20), nullable=False),
        sa.Column("message_type", sa.String(length=20), nullable=False),
        sa.Column("body_text", sa.Text(), nullable=True),
        sa.Column("body_text_te", sa.Text(), nullable=True),
        sa.Column("media_document_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("farmer_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("received_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("processed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("processing_status", sa.String(length=20), server_default="pending", nullable=False),
        sa.Column("raw_payload", postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["org_id"], ["organizations.id"], ondelete="RESTRICT"),
        sa.ForeignKeyConstraint(["media_document_id"], ["documents.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["farmer_id"], ["farmers.id"], ondelete="SET NULL"),
        sa.UniqueConstraint("org_id", "external_message_id", name="uq_whatsapp_messages_org_external"),
        sa.CheckConstraint("direction IN ('inbound','outbound')", name="ck_whatsapp_messages_direction"),
        sa.CheckConstraint(
            "processing_status IN ('pending','processed','failed','ignored')",
            name="ck_whatsapp_messages_processing_status",
        ),
    )
    op.create_index("ix_whatsapp_messages_org_received", "whatsapp_messages", ["org_id", "received_at"])
    op.create_index("ix_whatsapp_messages_from_phone", "whatsapp_messages", ["from_phone", "received_at"])
    op.create_index(
        "ix_whatsapp_messages_pending",
        "whatsapp_messages",
        ["processing_status"],
        postgresql_where=sa.text("processing_status = 'pending'"),
    )

    op.create_table(
        "ai_jobs",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("org_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("job_type", sa.String(length=50), nullable=False),
        sa.Column("status", sa.String(length=20), server_default="pending", nullable=False),
        sa.Column("input_type", sa.String(length=50), nullable=False),
        sa.Column("input_ref_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("document_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("whatsapp_message_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("model_provider", sa.String(length=50), nullable=True),
        sa.Column("model_name", sa.String(length=100), nullable=True),
        sa.Column("prompt_version", sa.String(length=50), nullable=True),
        sa.Column("confidence", sa.Numeric(5, 4), nullable=True),
        sa.Column("result", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column("error_message", sa.Text(), nullable=True),
        sa.Column("tokens_input", sa.Integer(), nullable=True),
        sa.Column("tokens_output", sa.Integer(), nullable=True),
        sa.Column("cost_usd", sa.Numeric(10, 6), nullable=True),
        sa.Column("started_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("completed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("created_by", postgresql.UUID(as_uuid=True), nullable=True),
        sa.ForeignKeyConstraint(["org_id"], ["organizations.id"], ondelete="RESTRICT"),
        sa.ForeignKeyConstraint(["document_id"], ["documents.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["whatsapp_message_id"], ["whatsapp_messages.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["created_by"], ["users.id"], ondelete="SET NULL"),
        sa.CheckConstraint(
            "status IN ('pending','processing','completed','failed','cancelled')",
            name="ck_ai_jobs_status",
        ),
        sa.CheckConstraint("confidence IS NULL OR (confidence >= 0 AND confidence <= 1)", name="ck_ai_jobs_confidence"),
    )
    op.create_index("ix_ai_jobs_org_status_created", "ai_jobs", ["org_id", "status", "created_at"])
    op.create_index("ix_ai_jobs_input", "ai_jobs", ["input_type", "input_ref_id"])

    op.create_table(
        "ai_suggestions",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("org_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("ai_job_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("target_entity_type", sa.String(length=50), nullable=False),
        sa.Column("suggested_payload", postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column("summary", sa.Text(), nullable=True),
        sa.Column("summary_te", sa.Text(), nullable=True),
        sa.Column("confidence", sa.Numeric(5, 4), nullable=True),
        sa.Column("status", sa.String(length=20), server_default="pending", nullable=False),
        sa.Column("reviewed_by", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("reviewed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("rejection_reason", sa.Text(), nullable=True),
        sa.Column("created_entity_type", sa.String(length=50), nullable=True),
        sa.Column("created_entity_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(["org_id"], ["organizations.id"], ondelete="RESTRICT"),
        sa.ForeignKeyConstraint(["ai_job_id"], ["ai_jobs.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["reviewed_by"], ["users.id"], ondelete="SET NULL"),
        sa.CheckConstraint("status IN ('pending','accepted','rejected','expired')", name="ck_ai_suggestions_status"),
    )
    op.create_index("ix_ai_suggestions_org_status_created", "ai_suggestions", ["org_id", "status", "created_at"])

    op.create_table(
        "ai_summaries",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("org_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("ai_job_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("entity_type", sa.String(length=50), nullable=False),
        sa.Column("entity_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("summary_type", sa.String(length=50), nullable=False),
        sa.Column("locale", sa.String(length=10), nullable=False),
        sa.Column("summary_text", sa.Text(), nullable=False),
        sa.Column("model_provider", sa.String(length=50), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["org_id"], ["organizations.id"], ondelete="RESTRICT"),
        sa.ForeignKeyConstraint(["ai_job_id"], ["ai_jobs.id"], ondelete="CASCADE"),
    )
    op.create_index(
        "ix_ai_summaries_entity_locale",
        "ai_summaries",
        ["entity_type", "entity_id", "locale", "created_at"],
    )

    op.create_table(
        "ocr_extractions",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("org_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("document_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("ai_job_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("document_type_detected", sa.String(length=50), nullable=True),
        sa.Column("raw_text", sa.Text(), nullable=True),
        sa.Column("raw_text_te", sa.Text(), nullable=True),
        sa.Column("extracted_fields", postgresql.JSONB(astext_type=sa.Text()), server_default="{}", nullable=False),
        sa.Column("field_confidence", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column("locale_detected", sa.String(length=10), nullable=True),
        sa.Column("status", sa.String(length=20), server_default="completed", nullable=False),
        sa.Column("reviewed_by", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("reviewed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("is_verified", sa.Boolean(), server_default=sa.text("false"), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["org_id"], ["organizations.id"], ondelete="RESTRICT"),
        sa.ForeignKeyConstraint(["document_id"], ["documents.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["ai_job_id"], ["ai_jobs.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["reviewed_by"], ["users.id"], ondelete="SET NULL"),
    )
    op.create_index("ix_ocr_extractions_document_id", "ocr_extractions", ["document_id"])
    op.create_index(
        "ix_ocr_extractions_fields",
        "ocr_extractions",
        ["extracted_fields"],
        postgresql_using="gin",
    )

    op.create_table(
        "voice_transcripts",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("org_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("document_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("ai_job_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("locale", sa.String(length=10), nullable=False),
        sa.Column("transcript", sa.Text(), nullable=False),
        sa.Column("transcript_te", sa.Text(), nullable=True),
        sa.Column("duration_seconds", sa.Numeric(10, 2), nullable=True),
        sa.Column("confidence", sa.Numeric(5, 4), nullable=True),
        sa.Column("intent", sa.String(length=50), nullable=True),
        sa.Column("extracted_entities", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("created_by", postgresql.UUID(as_uuid=True), nullable=True),
        sa.ForeignKeyConstraint(["org_id"], ["organizations.id"], ondelete="RESTRICT"),
        sa.ForeignKeyConstraint(["document_id"], ["documents.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["ai_job_id"], ["ai_jobs.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["created_by"], ["users.id"], ondelete="SET NULL"),
    )
    op.create_index("ix_voice_transcripts_document_id", "voice_transcripts", ["document_id"])


def downgrade() -> None:
    op.drop_index("ix_voice_transcripts_document_id", table_name="voice_transcripts")
    op.drop_table("voice_transcripts")
    op.drop_index("ix_ocr_extractions_fields", table_name="ocr_extractions")
    op.drop_index("ix_ocr_extractions_document_id", table_name="ocr_extractions")
    op.drop_table("ocr_extractions")
    op.drop_index("ix_ai_summaries_entity_locale", table_name="ai_summaries")
    op.drop_table("ai_summaries")
    op.drop_index("ix_ai_suggestions_org_status_created", table_name="ai_suggestions")
    op.drop_table("ai_suggestions")
    op.drop_index("ix_ai_jobs_input", table_name="ai_jobs")
    op.drop_index("ix_ai_jobs_org_status_created", table_name="ai_jobs")
    op.drop_table("ai_jobs")
    op.drop_index("ix_whatsapp_messages_pending", table_name="whatsapp_messages")
    op.drop_index("ix_whatsapp_messages_from_phone", table_name="whatsapp_messages")
    op.drop_index("ix_whatsapp_messages_org_received", table_name="whatsapp_messages")
    op.drop_table("whatsapp_messages")
