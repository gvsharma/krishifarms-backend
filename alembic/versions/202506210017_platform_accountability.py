"""Platform accountability: comments, tags, buyers, agents, vehicle types, crop prices."""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

from migration_utils import apply_updated_at_trigger, audit_columns, org_fk, users_fk

revision: str = "202506210017"
down_revision: Union[str, None] = "202506210016"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column("audit_logs", sa.Column("device_id", sa.String(length=100), nullable=True))
    op.add_column("audit_logs", sa.Column("client_type", sa.String(length=30), nullable=True))
    op.add_column("activity_feed", sa.Column("device_id", sa.String(length=100), nullable=True))
    op.add_column("activity_feed", sa.Column("client_type", sa.String(length=30), nullable=True))

    op.create_table(
        "entity_comments",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("org_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("entity_type", sa.String(length=50), nullable=False),
        sa.Column("entity_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("body", sa.Text(), nullable=False),
        sa.Column("body_te", sa.Text(), nullable=True),
        sa.Column("author_user_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("device_id", sa.String(length=100), nullable=True),
        sa.Column("client_type", sa.String(length=30), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True),
        org_fk(),
        users_fk("author_user_id", nullable=False),
    )
    op.create_index("ix_entity_comments_org_entity", "entity_comments", ["org_id", "entity_type", "entity_id"])
    op.create_index("ix_entity_comments_author", "entity_comments", ["author_user_id"])

    op.create_table(
        "entity_tags",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("org_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("entity_type", sa.String(length=50), nullable=False),
        sa.Column("entity_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("tag", sa.String(length=50), nullable=False),
        sa.Column("created_by", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("device_id", sa.String(length=100), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        org_fk(),
        users_fk("created_by", nullable=True),
        sa.UniqueConstraint("org_id", "entity_type", "entity_id", "tag", name="uq_entity_tags_org_entity_tag"),
    )
    op.create_index("ix_entity_tags_org_entity", "entity_tags", ["org_id", "entity_type", "entity_id"])

    op.create_table(
        "buyers",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("org_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("name", sa.String(length=200), nullable=False),
        sa.Column("name_te", sa.Text(), nullable=True),
        sa.Column("phone", sa.String(length=15), nullable=True),
        sa.Column("gstin", sa.String(length=20), nullable=True),
        sa.Column("contact_person", sa.String(length=200), nullable=True),
        sa.Column("address", sa.Text(), nullable=True),
        sa.Column("village_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column("is_active", sa.Boolean(), server_default=sa.text("true"), nullable=False),
        *audit_columns(),
        org_fk(),
        sa.ForeignKeyConstraint(["village_id"], ["villages.id"], ondelete="SET NULL"),
    )
    op.create_index("ix_buyers_org_id", "buyers", ["org_id"])
    apply_updated_at_trigger("buyers")

    op.create_table(
        "field_agents",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("org_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("name", sa.String(length=200), nullable=False),
        sa.Column("name_te", sa.Text(), nullable=True),
        sa.Column("phone", sa.String(length=15), nullable=True),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("village_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("commission_pct", sa.Numeric(5, 2), nullable=True),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column("is_active", sa.Boolean(), server_default=sa.text("true"), nullable=False),
        *audit_columns(),
        org_fk(),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["village_id"], ["villages.id"], ondelete="SET NULL"),
    )
    op.create_index("ix_field_agents_org_id", "field_agents", ["org_id"])
    apply_updated_at_trigger("field_agents")

    op.create_table(
        "vehicle_types",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("org_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("name", sa.String(length=100), nullable=False),
        sa.Column("name_te", sa.Text(), nullable=True),
        sa.Column("code", sa.String(length=50), nullable=False),
        sa.Column("capacity_quintals", sa.Numeric(10, 2), nullable=True),
        sa.Column("fuel_type", sa.String(length=30), nullable=True),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column("is_active", sa.Boolean(), server_default=sa.text("true"), nullable=False),
        *audit_columns(),
        org_fk(),
    )
    op.create_index(
        "uq_vehicle_types_org_code_active",
        "vehicle_types",
        ["org_id", "code"],
        unique=True,
        postgresql_where=sa.text("deleted_at IS NULL"),
    )
    apply_updated_at_trigger("vehicle_types")

    op.create_table(
        "crop_price_rules",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("org_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("crop_type_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("village_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("effective_from", sa.Date(), nullable=False),
        sa.Column("effective_to", sa.Date(), nullable=True),
        sa.Column("rate_per_quintal", sa.Numeric(14, 2), nullable=False),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column("is_active", sa.Boolean(), server_default=sa.text("true"), nullable=False),
        *audit_columns(),
        org_fk(),
        sa.ForeignKeyConstraint(["crop_type_id"], ["crop_types.id"], ondelete="RESTRICT"),
        sa.ForeignKeyConstraint(["village_id"], ["villages.id"], ondelete="SET NULL"),
    )
    op.create_index("ix_crop_price_rules_org_crop", "crop_price_rules", ["org_id", "crop_type_id"])
    apply_updated_at_trigger("crop_price_rules")


def downgrade() -> None:
    op.drop_index("ix_crop_price_rules_org_crop", table_name="crop_price_rules")
    op.execute("DROP TRIGGER IF EXISTS trg_crop_price_rules_updated_at ON crop_price_rules;")
    op.drop_table("crop_price_rules")
    op.execute("DROP TRIGGER IF EXISTS trg_vehicle_types_updated_at ON vehicle_types;")
    op.drop_index("uq_vehicle_types_org_code_active", table_name="vehicle_types")
    op.drop_table("vehicle_types")
    op.execute("DROP TRIGGER IF EXISTS trg_field_agents_updated_at ON field_agents;")
    op.drop_index("ix_field_agents_org_id", table_name="field_agents")
    op.drop_table("field_agents")
    op.execute("DROP TRIGGER IF EXISTS trg_buyers_updated_at ON buyers;")
    op.drop_index("ix_buyers_org_id", table_name="buyers")
    op.drop_table("buyers")
    op.drop_index("ix_entity_tags_org_entity", table_name="entity_tags")
    op.drop_table("entity_tags")
    op.drop_index("ix_entity_comments_author", table_name="entity_comments")
    op.drop_index("ix_entity_comments_org_entity", table_name="entity_comments")
    op.drop_table("entity_comments")
    op.drop_column("activity_feed", "client_type")
    op.drop_column("activity_feed", "device_id")
    op.drop_column("audit_logs", "client_type")
    op.drop_column("audit_logs", "device_id")
