"""Tenant-scoped direct messaging and realtime foundation.

Revision ID: 0005_realtime_messaging
"""

import sqlalchemy as sa

from alembic import op

revision = "0005_realtime_messaging"
down_revision = "0004_presence"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "conversations",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column(
            "tenant_id",
            sa.String(36),
            sa.ForeignKey("tenants.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("kind", sa.String(20), nullable=False),
        sa.Column("direct_key", sa.String(73), nullable=False),
        sa.Column(
            "created_by_user_id",
            sa.String(36),
            sa.ForeignKey("users.id", ondelete="RESTRICT"),
            nullable=False,
        ),
        sa.Column("last_message_at", sa.DateTime(timezone=True)),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.UniqueConstraint("tenant_id", "direct_key", name="uq_conversations_direct"),
        sa.CheckConstraint("kind = 'direct'", name="ck_conversations_kind"),
    )
    for column in ["tenant_id", "created_by_user_id", "last_message_at"]:
        op.create_index(f"ix_conversations_{column}", "conversations", [column])

    op.create_table(
        "conversation_participants",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column(
            "tenant_id",
            sa.String(36),
            sa.ForeignKey("tenants.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column(
            "conversation_id",
            sa.String(36),
            sa.ForeignKey("conversations.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column(
            "user_id",
            sa.String(36),
            sa.ForeignKey("users.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("joined_at", sa.DateTime(timezone=True), nullable=False),
        sa.UniqueConstraint("conversation_id", "user_id", name="uq_conversation_participant"),
    )
    for column in ["tenant_id", "conversation_id", "user_id"]:
        op.create_index(
            f"ix_conversation_participants_{column}",
            "conversation_participants",
            [column],
        )

    op.create_table(
        "messages",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column(
            "tenant_id",
            sa.String(36),
            sa.ForeignKey("tenants.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column(
            "conversation_id",
            sa.String(36),
            sa.ForeignKey("conversations.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column(
            "sender_user_id",
            sa.String(36),
            sa.ForeignKey("users.id", ondelete="RESTRICT"),
            nullable=False,
        ),
        sa.Column("client_message_id", sa.String(64), nullable=False),
        sa.Column("sequence_number", sa.Integer(), nullable=False),
        sa.Column("body", sa.Text(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("deleted_at", sa.DateTime(timezone=True)),
        sa.UniqueConstraint("conversation_id", "sequence_number", name="uq_messages_sequence"),
        sa.UniqueConstraint(
            "tenant_id",
            "sender_user_id",
            "client_message_id",
            name="uq_messages_client_id",
        ),
        sa.CheckConstraint(
            "length(body) >= 1 AND length(body) <= 4000",
            name="ck_messages_body_length",
        ),
    )
    for column in [
        "tenant_id",
        "conversation_id",
        "sender_user_id",
        "created_at",
        "expires_at",
    ]:
        op.create_index(f"ix_messages_{column}", "messages", [column])

    op.create_table(
        "message_receipts",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column(
            "tenant_id",
            sa.String(36),
            sa.ForeignKey("tenants.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column(
            "message_id",
            sa.String(36),
            sa.ForeignKey("messages.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column(
            "user_id",
            sa.String(36),
            sa.ForeignKey("users.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("read_at", sa.DateTime(timezone=True), nullable=False),
        sa.UniqueConstraint("message_id", "user_id", name="uq_message_receipt"),
    )
    for column in ["tenant_id", "message_id", "user_id"]:
        op.create_index(f"ix_message_receipts_{column}", "message_receipts", [column])

    op.bulk_insert(
        sa.table(
            "permissions",
            sa.column("id", sa.String),
            sa.column("code", sa.String),
            sa.column("description", sa.String),
        ),
        [
            {
                "id": "00000000-0000-0000-0000-000000000012",
                "code": "message.metadata.read",
                "description": "Read aggregate tenant messaging metadata",
            },
            {
                "id": "00000000-0000-0000-0000-000000000013",
                "code": "message.retention.manage",
                "description": "Purge expired tenant messages",
            },
        ],
    )


def downgrade() -> None:
    op.drop_table("message_receipts")
    op.drop_table("messages")
    op.drop_table("conversation_participants")
    op.drop_table("conversations")
    op.execute(
        sa.text(
            "DELETE FROM role_permissions WHERE permission_id IN "
            "(SELECT id FROM permissions WHERE code IN "
            "('message.metadata.read', 'message.retention.manage'))"
        )
    )
    op.execute(
        sa.text(
            "DELETE FROM permissions WHERE code IN "
            "('message.metadata.read', 'message.retention.manage')"
        )
    )
