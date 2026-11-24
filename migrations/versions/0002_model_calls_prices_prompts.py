"""Model calls, price versions and prompt versions; prompt link on agent configs.

Revision ID: 0002
Revises: 0001
Create Date: 2026-11-23 00:45:39.567205
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "0002"
down_revision: str | None = "0001"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "price_versions",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("provider", sa.String(length=50), nullable=False),
        sa.Column("model", sa.String(length=200), nullable=False),
        sa.Column(
            "input_usd_per_million", sa.Numeric(precision=14, scale=6), nullable=False
        ),
        sa.Column(
            "cached_input_usd_per_million",
            sa.Numeric(precision=14, scale=6),
            nullable=True,
        ),
        sa.Column(
            "output_usd_per_million", sa.Numeric(precision=14, scale=6), nullable=False
        ),
        sa.Column("currency", sa.String(length=3), nullable=False),
        sa.Column("effective_date", sa.Date(), nullable=False),
        sa.Column("source", sa.String(length=200), nullable=False),
        sa.Column("content_hash", sa.String(length=64), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_price_versions")),
        sa.UniqueConstraint(
            "content_hash", name=op.f("uq_price_versions_content_hash")
        ),
    )
    op.create_index(
        op.f("ix_price_versions_model"), "price_versions", ["model"], unique=False
    )
    op.create_table(
        "prompt_versions",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("name", sa.String(length=100), nullable=False),
        sa.Column("content", sa.Text(), nullable=False),
        sa.Column("content_hash", sa.String(length=64), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_prompt_versions")),
        sa.UniqueConstraint(
            "content_hash", name=op.f("uq_prompt_versions_content_hash")
        ),
    )
    op.create_table(
        "model_calls",
        sa.Column("id", sa.BigInteger(), sa.Identity(always=True), nullable=False),
        sa.Column("attempt_id", sa.Uuid(), nullable=False),
        sa.Column("sequence", sa.Integer(), nullable=False),
        sa.Column("turn", sa.Integer(), nullable=False),
        sa.Column("try_number", sa.Integer(), nullable=False),
        sa.Column("requested_model", sa.String(length=200), nullable=False),
        sa.Column("resolved_model", sa.String(length=200), nullable=True),
        sa.Column(
            "status",
            sa.Enum(
                "ok",
                "retried",
                "failed",
                name="modelcallstatus",
                native_enum=False,
                length=32,
            ),
            nullable=False,
        ),
        sa.Column("input_tokens", sa.Integer(), nullable=True),
        sa.Column("output_tokens", sa.Integer(), nullable=True),
        sa.Column("cached_input_tokens", sa.Integer(), nullable=True),
        sa.Column(
            "estimated_cost_usd", sa.Numeric(precision=14, scale=8), nullable=True
        ),
        sa.Column("price_version_id", sa.Uuid(), nullable=True),
        sa.Column("latency_ms", sa.Double(), nullable=False),
        sa.Column("backoff_ms", sa.Double(), nullable=False),
        sa.Column("error", sa.Text(), nullable=True),
        sa.Column("started_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(
            ["attempt_id"],
            ["attempts.id"],
            name=op.f("fk_model_calls_attempt_id_attempts"),
            ondelete="CASCADE",
        ),
        sa.ForeignKeyConstraint(
            ["price_version_id"],
            ["price_versions.id"],
            name=op.f("fk_model_calls_price_version_id_price_versions"),
            ondelete="RESTRICT",
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_model_calls")),
        sa.UniqueConstraint("attempt_id", "sequence", name="uq_model_calls_sequence"),
    )
    op.create_index(
        op.f("ix_model_calls_requested_model"),
        "model_calls",
        ["requested_model"],
        unique=False,
    )
    op.create_index(
        op.f("ix_model_calls_status"), "model_calls", ["status"], unique=False
    )
    op.add_column(
        "agent_configs", sa.Column("prompt_version_id", sa.Uuid(), nullable=True)
    )
    op.create_index(
        op.f("ix_agent_configs_prompt_version_id"),
        "agent_configs",
        ["prompt_version_id"],
        unique=False,
    )
    op.create_foreign_key(
        op.f("fk_agent_configs_prompt_version_id_prompt_versions"),
        "agent_configs",
        "prompt_versions",
        ["prompt_version_id"],
        ["id"],
        ondelete="RESTRICT",
    )


def downgrade() -> None:
    op.drop_constraint(
        op.f("fk_agent_configs_prompt_version_id_prompt_versions"),
        "agent_configs",
        type_="foreignkey",
    )
    op.drop_index(
        op.f("ix_agent_configs_prompt_version_id"), table_name="agent_configs"
    )
    op.drop_column("agent_configs", "prompt_version_id")
    op.drop_index(op.f("ix_model_calls_status"), table_name="model_calls")
    op.drop_index(op.f("ix_model_calls_requested_model"), table_name="model_calls")
    op.drop_table("model_calls")
    op.drop_table("prompt_versions")
    op.drop_index(op.f("ix_price_versions_model"), table_name="price_versions")
    op.drop_table("price_versions")
