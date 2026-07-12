"""District / mandal masters + village FK hierarchy."""

from typing import Sequence, Union
from uuid import uuid4

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "202506210023"
down_revision: Union[str, None] = "202506210022"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "districts",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("org_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("name", sa.String(length=100), nullable=False),
        sa.Column("state", sa.String(length=100), nullable=True),
        sa.Column("created_by", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("updated_by", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["org_id"], ["organizations.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("org_id", "name", name="uq_districts_org_name"),
    )
    op.create_index("ix_districts_org_id", "districts", ["org_id"])

    op.create_table(
        "mandals",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("org_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("district_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("name", sa.String(length=100), nullable=False),
        sa.Column("created_by", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("updated_by", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["org_id"], ["organizations.id"]),
        sa.ForeignKeyConstraint(["district_id"], ["districts.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("org_id", "district_id", "name", name="uq_mandals_org_district_name"),
    )
    op.create_index("ix_mandals_org_id", "mandals", ["org_id"])
    op.create_index("ix_mandals_district_id", "mandals", ["district_id"])

    op.add_column("villages", sa.Column("district_id", postgresql.UUID(as_uuid=True), nullable=True))
    op.add_column("villages", sa.Column("mandal_id", postgresql.UUID(as_uuid=True), nullable=True))
    op.create_foreign_key("fk_villages_district_id", "villages", "districts", ["district_id"], ["id"])
    op.create_foreign_key("fk_villages_mandal_id", "villages", "mandals", ["mandal_id"], ["id"])
    op.create_index("ix_villages_district_id", "villages", ["district_id"])
    op.create_index("ix_villages_mandal_id", "villages", ["mandal_id"])

    op.drop_constraint("uq_villages_org_name", "villages", type_="unique")
    op.create_unique_constraint(
        "uq_villages_org_mandal_name",
        "villages",
        ["org_id", "mandal", "name"],
    )

    # Backfill districts / mandals from existing denormalized village strings.
    conn = op.get_bind()
    org_rows = conn.execute(sa.text("SELECT id FROM organizations")).fetchall()
    for org_row in org_rows:
        org_id = str(org_row.id)
        district_pairs = conn.execute(
            sa.text(
                """
                SELECT DISTINCT district, state
                FROM villages
                WHERE org_id = :org_id
                  AND deleted_at IS NULL
                  AND district IS NOT NULL
                  AND btrim(district) <> ''
                """
            ),
            {"org_id": org_id},
        ).fetchall()
        district_ids: dict[str, str] = {}
        for district_name, state in district_pairs:
            district_id = str(uuid4())
            conn.execute(
                sa.text(
                    """
                    INSERT INTO districts (id, org_id, name, state, created_at, updated_at)
                    VALUES (:id, :org_id, :name, :state, now(), now())
                    ON CONFLICT (org_id, name) DO NOTHING
                    """
                ),
                {
                    "id": district_id,
                    "org_id": org_id,
                    "name": district_name,
                    "state": state,
                },
            )
            row = conn.execute(
                sa.text(
                    """
                    SELECT id FROM districts
                    WHERE org_id = :org_id AND name = :name AND deleted_at IS NULL
                    """
                ),
                {"org_id": org_id, "name": district_name},
            ).fetchone()
            if row:
                district_ids[district_name] = str(row.id)

        mandal_pairs = conn.execute(
            sa.text(
                """
                SELECT DISTINCT mandal, district
                FROM villages
                WHERE org_id = :org_id
                  AND deleted_at IS NULL
                  AND mandal IS NOT NULL
                  AND btrim(mandal) <> ''
                  AND district IS NOT NULL
                  AND btrim(district) <> ''
                """
            ),
            {"org_id": org_id},
        ).fetchall()
        for mandal_name, district_name in mandal_pairs:
            district_id = district_ids.get(district_name)
            if not district_id:
                continue
            mandal_id = str(uuid4())
            conn.execute(
                sa.text(
                    """
                    INSERT INTO mandals (id, org_id, district_id, name, created_at, updated_at)
                    VALUES (:id, :org_id, :district_id, :name, now(), now())
                    ON CONFLICT (org_id, district_id, name) DO NOTHING
                    """
                ),
                {
                    "id": mandal_id,
                    "org_id": org_id,
                    "district_id": district_id,
                    "name": mandal_name,
                },
            )

        conn.execute(
            sa.text(
                """
                UPDATE villages v
                SET district_id = d.id
                FROM districts d
                WHERE v.org_id = :org_id
                  AND d.org_id = v.org_id
                  AND v.district = d.name
                  AND v.deleted_at IS NULL
                  AND d.deleted_at IS NULL
                  AND v.district_id IS NULL
                """
            ),
            {"org_id": org_id},
        )
        conn.execute(
            sa.text(
                """
                UPDATE villages v
                SET mandal_id = m.id
                FROM mandals m
                WHERE v.org_id = :org_id
                  AND m.org_id = v.org_id
                  AND v.mandal = m.name
                  AND v.district_id = m.district_id
                  AND v.deleted_at IS NULL
                  AND m.deleted_at IS NULL
                  AND v.mandal_id IS NULL
                """
            ),
            {"org_id": org_id},
        )


def downgrade() -> None:
    op.drop_constraint("uq_villages_org_mandal_name", "villages", type_="unique")
    op.create_unique_constraint("uq_villages_org_name", "villages", ["org_id", "name"])
    op.drop_index("ix_villages_mandal_id", table_name="villages")
    op.drop_index("ix_villages_district_id", table_name="villages")
    op.drop_constraint("fk_villages_mandal_id", "villages", type_="foreignkey")
    op.drop_constraint("fk_villages_district_id", "villages", type_="foreignkey")
    op.drop_column("villages", "mandal_id")
    op.drop_column("villages", "district_id")
    op.drop_index("ix_mandals_district_id", table_name="mandals")
    op.drop_index("ix_mandals_org_id", table_name="mandals")
    op.drop_table("mandals")
    op.drop_index("ix_districts_org_id", table_name="districts")
    op.drop_table("districts")
