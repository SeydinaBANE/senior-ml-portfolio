"""initial schema

Revision ID: 0001
Revises:
Create Date: 2026-06-22
"""

from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

revision: str = "0001"
down_revision: str | None = None
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "users",
        sa.Column("id", sa.Uuid(), primary_key=True),
        sa.Column("email", sa.String(255), nullable=False, unique=True),
        sa.Column("hashed_password", sa.String(255), nullable=False),
        sa.Column("role", sa.String(50), nullable=False, server_default="user"),
        sa.Column("tenant_id", sa.Uuid(), nullable=False),
        sa.Column("is_active", sa.Boolean(), server_default=sa.true()),
        sa.Column("created_at", sa.DateTime(), server_default=sa.func.now()),
    )

    op.create_table(
        "agent_definitions",
        sa.Column("id", sa.Uuid(), primary_key=True),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("description", sa.Text(), server_default=""),
        sa.Column("category", sa.String(100), nullable=False),
        sa.Column("system_prompt", sa.Text(), nullable=False),
        sa.Column("tools", sa.JSON(), server_default="[]"),
        sa.Column("model", sa.String(100), server_default="gpt-4o"),
        sa.Column("is_public", sa.Boolean(), server_default=sa.false()),
        sa.Column("owner_id", sa.Uuid(), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("tenant_id", sa.Uuid(), nullable=False),
        sa.Column("tags", sa.JSON(), server_default="[]"),
        sa.Column("created_at", sa.DateTime(), server_default=sa.func.now()),
    )

    op.create_table(
        "usage_events",
        sa.Column("id", sa.Uuid(), primary_key=True),
        sa.Column("tenant_id", sa.Uuid(), nullable=False),
        sa.Column("user_id", sa.Uuid(), sa.ForeignKey("users.id"), nullable=False),
        sa.Column(
            "agent_id", sa.Uuid(), sa.ForeignKey("agent_definitions.id"), nullable=False
        ),
        sa.Column("input_tokens", sa.Integer(), server_default="0"),
        sa.Column("output_tokens", sa.Integer(), server_default="0"),
        sa.Column("cost_usd", sa.Float(), server_default="0.0"),
        sa.Column("latency_ms", sa.Integer(), server_default="0"),
        sa.Column("occurred_at", sa.DateTime(), server_default=sa.func.now()),
    )

    op.create_index("ix_users_email", "users", ["email"])
    op.create_index("ix_agent_definitions_tenant", "agent_definitions", ["tenant_id"])
    op.create_index("ix_usage_events_tenant", "usage_events", ["tenant_id"])
    op.create_index("ix_usage_events_occurred_at", "usage_events", ["occurred_at"])


def downgrade() -> None:
    op.drop_table("usage_events")
    op.drop_table("agent_definitions")
    op.drop_table("users")
