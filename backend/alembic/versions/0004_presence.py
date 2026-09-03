"""Tenant-scoped workforce presence.

Revision ID: 0004_presence
"""

import sqlalchemy as sa

from alembic import op

revision = "0004_presence"
down_revision = "0003_workforce_operations"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "presences",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column(
            "tenant_id",
            sa.String(36),
            sa.ForeignKey("tenants.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column(
            "user_id",
            sa.String(36),
            sa.ForeignKey("users.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("status", sa.String(20), nullable=False),
        sa.Column("last_seen_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.UniqueConstraint("tenant_id", "user_id"),
        sa.CheckConstraint(
            "status IN ('available', 'away', 'busy', 'offline')",
            name="ck_presences_status",
        ),
    )
    for column in ["tenant_id", "user_id", "status", "expires_at"]:
        op.create_index(f"ix_presences_{column}", "presences", [column])


def downgrade() -> None:
    op.drop_table("presences")
