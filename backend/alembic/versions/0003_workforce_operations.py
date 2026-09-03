"""Workforce operations.

Revision ID: 0003_workforce_operations
"""

import sqlalchemy as sa

from alembic import op

revision = "0003_workforce_operations"
down_revision = "0002_admin_security"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("departments", sa.Column("manager_employee_id", sa.String(36)))
    op.create_index("ix_departments_manager_employee_id", "departments", ["manager_employee_id"])
    op.create_table(
        "invitations",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column(
            "tenant_id",
            sa.String(36),
            sa.ForeignKey("tenants.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("email", sa.String(320), nullable=False),
        sa.Column("token_digest", sa.String(64), nullable=False, unique=True),
        sa.Column("role_ids", sa.JSON(), nullable=False),
        sa.Column(
            "invited_by_user_id",
            sa.String(36),
            sa.ForeignKey("users.id", ondelete="RESTRICT"),
            nullable=False,
        ),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("accepted_at", sa.DateTime(timezone=True)),
        sa.Column("revoked_at", sa.DateTime(timezone=True)),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.UniqueConstraint("tenant_id", "email", "accepted_at"),
    )
    for column in ["tenant_id", "email", "invited_by_user_id", "created_at"]:
        op.create_index(f"ix_invitations_{column}", "invitations", [column])
    op.bulk_insert(
        sa.table(
            "permissions",
            sa.column("id", sa.String),
            sa.column("code", sa.String),
            sa.column("description", sa.String),
        ),
        [
            {
                "id": "00000000-0000-0000-0000-000000000011",
                "code": "membership.manage",
                "description": "Manage tenant invitations",
            }
        ],
    )


def downgrade() -> None:
    op.execute(sa.text("DELETE FROM permissions WHERE code = 'membership.manage'"))
    op.drop_table("invitations")
    op.drop_index("ix_departments_manager_employee_id", table_name="departments")
    op.drop_column("departments", "manager_employee_id")
