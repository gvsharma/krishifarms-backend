"""FCM push tokens per user device."""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

from migration_utils import org_fk, users_fk

revision: str = "202506210020"
down_revision: Union[str, None] = "202506210019"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "user_device_tokens",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("org_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("device_id", sa.String(length=100), nullable=False),
        sa.Column("fcm_token", sa.String(length=512), nullable=False),
        sa.Column("platform", sa.String(length=30), nullable=False, server_default="android"),
        sa.Column("app_version", sa.String(length=50), nullable=True),
        sa.Column("last_seen_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("revoked_at", sa.DateTime(timezone=True), nullable=True),
        org_fk(),
        users_fk("user_id", nullable=False),
        sa.UniqueConstraint("org_id", "fcm_token", name="uq_user_device_tokens_org_fcm"),
    )
    op.create_index("ix_user_device_tokens_user_device", "user_device_tokens", ["user_id", "device_id"])
    op.create_index("ix_user_device_tokens_user_active", "user_device_tokens", ["user_id", "revoked_at"])


def downgrade() -> None:
    op.drop_index("ix_user_device_tokens_user_active", table_name="user_device_tokens")
    op.drop_index("ix_user_device_tokens_user_device", table_name="user_device_tokens")
    op.drop_table("user_device_tokens")
