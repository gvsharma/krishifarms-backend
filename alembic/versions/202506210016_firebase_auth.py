"""Firebase phone auth columns on users."""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "202506210016"
down_revision: Union[str, None] = "202506210015"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column("users", sa.Column("firebase_uid", sa.String(length=128), nullable=True))
    op.add_column("users", sa.Column("village_id", postgresql.UUID(as_uuid=True), nullable=True))
    op.create_foreign_key(
        "fk_users_village_id_villages",
        "users",
        "villages",
        ["village_id"],
        ["id"],
        ondelete="SET NULL",
    )
    op.create_index(
        "uq_users_firebase_uid_active",
        "users",
        ["firebase_uid"],
        unique=True,
        postgresql_where=sa.text("deleted_at IS NULL AND firebase_uid IS NOT NULL"),
    )
    op.alter_column("users", "password_hash", existing_type=sa.String(length=255), nullable=True)


def downgrade() -> None:
    op.alter_column("users", "password_hash", existing_type=sa.String(length=255), nullable=False)
    op.drop_index("uq_users_firebase_uid_active", table_name="users")
    op.drop_constraint("fk_users_village_id_villages", "users", type_="foreignkey")
    op.drop_column("users", "village_id")
    op.drop_column("users", "firebase_uid")
