"""Farmer management tables."""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

from migration_utils import audit_columns, org_fk

revision: str = "202506210004"
down_revision: Union[str, None] = "202506210003"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "farmers",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("org_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("farmer_code", sa.String(length=50), nullable=False),
        sa.Column("full_name", sa.String(length=200), nullable=False),
        sa.Column("full_name_te", sa.Text(), nullable=True),
        sa.Column("father_name", sa.String(length=200), nullable=True),
        sa.Column("father_name_te", sa.Text(), nullable=True),
        sa.Column("phone_primary", sa.String(length=20), nullable=False),
        sa.Column("phone_secondary", sa.String(length=20), nullable=True),
        sa.Column("village_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("address", sa.Text(), nullable=True),
        sa.Column("address_te", sa.Text(), nullable=True),
        sa.Column("aadhaar_last4", sa.CHAR(length=4), nullable=True),
        sa.Column("pan_encrypted", sa.LargeBinary(), nullable=True),
        sa.Column("status", sa.String(length=20), server_default="active", nullable=False),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column(
            "search_vector",
            postgresql.TSVECTOR(),
            sa.Computed(
                "to_tsvector('simple', coalesce(full_name,'') || ' ' || coalesce(full_name_te,'') || ' ' || coalesce(phone_primary,''))",
                persisted=True,
            ),
            nullable=True,
        ),
        *audit_columns(),
        org_fk(),
        sa.ForeignKeyConstraint(["village_id"], ["villages.id"], ondelete="RESTRICT"),
        sa.CheckConstraint("status IN ('active','inactive','blocked')", name="ck_farmers_status"),
    )
    op.create_index(
        "uq_farmers_org_code_active",
        "farmers",
        ["org_id", "farmer_code"],
        unique=True,
        postgresql_where=sa.text("deleted_at IS NULL"),
    )
    op.create_index("ix_farmers_org_village", "farmers", ["org_id", "village_id"])
    op.create_index("ix_farmers_search_vector", "farmers", ["search_vector"], postgresql_using="gin")
    op.execute(
        "CREATE INDEX ix_farmers_full_name_trgm ON farmers USING gin (full_name gin_trgm_ops);"
    )
    op.execute(
        "CREATE INDEX ix_farmers_full_name_te_trgm ON farmers USING gin (full_name_te gin_trgm_ops);"
    )

    op.create_table(
        "farmer_bank_accounts",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("org_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("farmer_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("account_holder_name", sa.String(length=200), nullable=False),
        sa.Column("bank_name", sa.String(length=200), nullable=False),
        sa.Column("branch", sa.String(length=200), nullable=True),
        sa.Column("ifsc", sa.CHAR(length=11), nullable=False),
        sa.Column("account_number_encrypted", sa.LargeBinary(), nullable=False),
        sa.Column("is_primary", sa.Boolean(), server_default=sa.text("false"), nullable=False),
        *audit_columns(),
        org_fk(),
        sa.ForeignKeyConstraint(["farmer_id"], ["farmers.id"], ondelete="RESTRICT"),
    )
    op.create_index("ix_farmer_bank_accounts_farmer_id", "farmer_bank_accounts", ["farmer_id"])
    op.create_index(
        "uq_farmer_bank_accounts_primary_active",
        "farmer_bank_accounts",
        ["farmer_id"],
        unique=True,
        postgresql_where=sa.text("is_primary IS TRUE AND deleted_at IS NULL"),
    )

    op.create_table(
        "farmer_land_parcels",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("org_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("farmer_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("survey_number", sa.String(length=100), nullable=False),
        sa.Column("acres", sa.Numeric(10, 3), nullable=False),
        sa.Column("land_type", sa.String(length=50), nullable=True),
        sa.Column("location_notes", sa.Text(), nullable=True),
        sa.Column("geo_lat", sa.Numeric(10, 7), nullable=True),
        sa.Column("geo_lng", sa.Numeric(10, 7), nullable=True),
        *audit_columns(),
        org_fk(),
        sa.ForeignKeyConstraint(["farmer_id"], ["farmers.id"], ondelete="RESTRICT"),
        sa.CheckConstraint("acres > 0", name="ck_farmer_land_parcels_acres"),
    )
    op.create_index("ix_farmer_land_parcels_farmer_id", "farmer_land_parcels", ["farmer_id"])

    op.create_table(
        "farmer_crop_history",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("org_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("farmer_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("crop_type_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("season", sa.String(length=50), nullable=False),
        sa.Column("year", sa.SmallInteger(), nullable=False),
        sa.Column("acres", sa.Numeric(10, 3), nullable=True),
        sa.Column("notes", sa.Text(), nullable=True),
        *audit_columns(),
        org_fk(),
        sa.ForeignKeyConstraint(["farmer_id"], ["farmers.id"], ondelete="RESTRICT"),
        sa.ForeignKeyConstraint(["crop_type_id"], ["crop_types.id"], ondelete="RESTRICT"),
    )
    op.create_index("ix_farmer_crop_history_farmer_id", "farmer_crop_history", ["farmer_id"])

    for table in ("farmers", "farmer_bank_accounts", "farmer_land_parcels", "farmer_crop_history"):
        op.execute(
            f"""
            CREATE TRIGGER trg_{table}_updated_at
            BEFORE UPDATE ON {table}
            FOR EACH ROW EXECUTE FUNCTION set_updated_at();
            """
        )


def downgrade() -> None:
    for table in ("farmer_crop_history", "farmer_land_parcels", "farmer_bank_accounts", "farmers"):
        op.execute(f"DROP TRIGGER IF EXISTS trg_{table}_updated_at ON {table};")
    op.drop_index("ix_farmer_crop_history_farmer_id", table_name="farmer_crop_history")
    op.drop_table("farmer_crop_history")
    op.drop_index("ix_farmer_land_parcels_farmer_id", table_name="farmer_land_parcels")
    op.drop_table("farmer_land_parcels")
    op.drop_index("uq_farmer_bank_accounts_primary_active", table_name="farmer_bank_accounts")
    op.drop_index("ix_farmer_bank_accounts_farmer_id", table_name="farmer_bank_accounts")
    op.drop_table("farmer_bank_accounts")
    op.execute("DROP INDEX IF EXISTS ix_farmers_full_name_te_trgm;")
    op.execute("DROP INDEX IF EXISTS ix_farmers_full_name_trgm;")
    op.drop_index("ix_farmers_search_vector", table_name="farmers")
    op.drop_index("ix_farmers_org_village", table_name="farmers")
    op.drop_index("uq_farmers_org_code_active", table_name="farmers")
    op.drop_table("farmers")
