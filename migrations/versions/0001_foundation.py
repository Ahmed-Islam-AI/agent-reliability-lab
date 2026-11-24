"""Foundation tables: datasets, tasks, agents, experiments, runs, attempts, traces.

Revision ID: 0001
Revises:
Create Date: 2026-11-18 12:34:04.376432
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "0001"
down_revision: str | None = None
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "agent_configs",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("name", sa.String(length=200), nullable=False),
        sa.Column("adapter", sa.String(length=50), nullable=False),
        sa.Column("settings", postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column("content_hash", sa.String(length=64), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_agent_configs")),
        sa.UniqueConstraint("content_hash", name=op.f("uq_agent_configs_content_hash")),
    )
    op.create_table(
        "datasets",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("name", sa.String(length=100), nullable=False),
        sa.Column("domain", sa.String(length=50), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_datasets")),
        sa.UniqueConstraint("name", name=op.f("uq_datasets_name")),
    )
    op.create_table(
        "dataset_versions",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("dataset_id", sa.Uuid(), nullable=False),
        sa.Column("version", sa.Integer(), nullable=False),
        sa.Column("content_hash", sa.String(length=64), nullable=False),
        sa.Column("manifest", postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column(
            "base_world", postgresql.JSONB(astext_type=sa.Text()), nullable=False
        ),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(
            ["dataset_id"],
            ["datasets.id"],
            name=op.f("fk_dataset_versions_dataset_id_datasets"),
            ondelete="RESTRICT",
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_dataset_versions")),
        sa.UniqueConstraint(
            "dataset_id", "content_hash", name="uq_dataset_versions_content"
        ),
        sa.UniqueConstraint(
            "dataset_id", "version", name="uq_dataset_versions_version"
        ),
    )
    op.create_index(
        op.f("ix_dataset_versions_dataset_id"),
        "dataset_versions",
        ["dataset_id"],
        unique=False,
    )
    op.create_table(
        "experiments",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("name", sa.String(length=200), nullable=False),
        sa.Column("dataset_version_id", sa.Uuid(), nullable=False),
        sa.Column(
            "status",
            sa.Enum(
                "running",
                "completed",
                name="experimentstatus",
                native_enum=False,
                length=32,
            ),
            nullable=False,
        ),
        sa.Column("manifest", postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column("finished_at", sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(
            ["dataset_version_id"],
            ["dataset_versions.id"],
            name=op.f("fk_experiments_dataset_version_id_dataset_versions"),
            ondelete="RESTRICT",
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_experiments")),
    )
    op.create_index(
        op.f("ix_experiments_dataset_version_id"),
        "experiments",
        ["dataset_version_id"],
        unique=False,
    )
    op.create_index(
        op.f("ix_experiments_status"), "experiments", ["status"], unique=False
    )
    op.create_table(
        "task_versions",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("dataset_version_id", sa.Uuid(), nullable=False),
        sa.Column("task_id", sa.String(length=100), nullable=False),
        sa.Column("task_version", sa.Integer(), nullable=False),
        sa.Column("family", sa.String(length=100), nullable=False),
        sa.Column("category", sa.String(length=50), nullable=False),
        sa.Column("content_hash", sa.String(length=64), nullable=False),
        sa.Column(
            "definition", postgresql.JSONB(astext_type=sa.Text()), nullable=False
        ),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(
            ["dataset_version_id"],
            ["dataset_versions.id"],
            name=op.f("fk_task_versions_dataset_version_id_dataset_versions"),
            ondelete="RESTRICT",
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_task_versions")),
        sa.UniqueConstraint(
            "dataset_version_id", "task_id", name="uq_task_versions_task"
        ),
    )
    op.create_index(
        op.f("ix_task_versions_category"), "task_versions", ["category"], unique=False
    )
    op.create_index(
        op.f("ix_task_versions_dataset_version_id"),
        "task_versions",
        ["dataset_version_id"],
        unique=False,
    )
    op.create_table(
        "runs",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("experiment_id", sa.Uuid(), nullable=False),
        sa.Column("agent_config_id", sa.Uuid(), nullable=False),
        sa.Column("task_version_id", sa.Uuid(), nullable=False),
        sa.Column("repetition", sa.Integer(), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(
            ["agent_config_id"],
            ["agent_configs.id"],
            name=op.f("fk_runs_agent_config_id_agent_configs"),
            ondelete="RESTRICT",
        ),
        sa.ForeignKeyConstraint(
            ["experiment_id"],
            ["experiments.id"],
            name=op.f("fk_runs_experiment_id_experiments"),
            ondelete="CASCADE",
        ),
        sa.ForeignKeyConstraint(
            ["task_version_id"],
            ["task_versions.id"],
            name=op.f("fk_runs_task_version_id_task_versions"),
            ondelete="RESTRICT",
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_runs")),
        sa.UniqueConstraint(
            "experiment_id",
            "agent_config_id",
            "task_version_id",
            "repetition",
            name="uq_runs_plan",
        ),
    )
    op.create_index(
        op.f("ix_runs_agent_config_id"), "runs", ["agent_config_id"], unique=False
    )
    op.create_index(
        op.f("ix_runs_experiment_id"), "runs", ["experiment_id"], unique=False
    )
    op.create_index(
        op.f("ix_runs_task_version_id"), "runs", ["task_version_id"], unique=False
    )
    op.create_table(
        "attempts",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("run_id", sa.Uuid(), nullable=False),
        sa.Column("attempt_number", sa.Integer(), nullable=False),
        sa.Column(
            "execution_status",
            sa.Enum(
                "running",
                "completed",
                "infrastructure_error",
                name="executionstatus",
                native_enum=False,
                length=32,
            ),
            nullable=False,
        ),
        sa.Column(
            "evaluation_status",
            sa.Enum(
                "pending",
                "pass",
                "fail",
                "not_applicable",
                "evaluation_error",
                "not_scored",
                name="evaluationstatus",
                native_enum=False,
                length=32,
            ),
            nullable=False,
        ),
        sa.Column(
            "stop_reason",
            sa.Enum(
                "final_answer", "error", name="stopreason", native_enum=False, length=32
            ),
            nullable=True,
        ),
        sa.Column("final_response", sa.Text(), nullable=True),
        sa.Column(
            "final_snapshot", postgresql.JSONB(astext_type=sa.Text()), nullable=True
        ),
        sa.Column("error", sa.Text(), nullable=True),
        sa.Column(
            "started_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column("finished_at", sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(
            ["run_id"],
            ["runs.id"],
            name=op.f("fk_attempts_run_id_runs"),
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_attempts")),
        sa.UniqueConstraint("run_id", "attempt_number", name="uq_attempts_number"),
    )
    op.create_index(
        op.f("ix_attempts_evaluation_status"),
        "attempts",
        ["evaluation_status"],
        unique=False,
    )
    op.create_index(
        op.f("ix_attempts_execution_status"),
        "attempts",
        ["execution_status"],
        unique=False,
    )
    op.create_index(op.f("ix_attempts_run_id"), "attempts", ["run_id"], unique=False)
    op.create_table(
        "scores",
        sa.Column("id", sa.BigInteger(), sa.Identity(always=True), nullable=False),
        sa.Column("attempt_id", sa.Uuid(), nullable=False),
        sa.Column("evaluator", sa.String(length=100), nullable=False),
        sa.Column("evaluator_version", sa.String(length=20), nullable=False),
        sa.Column("dimension", sa.String(length=100), nullable=False),
        sa.Column("applicable", sa.Boolean(), nullable=False),
        sa.Column(
            "status",
            sa.Enum(
                "pass",
                "fail",
                "not_applicable",
                "error",
                name="scorestatus",
                native_enum=False,
                length=32,
            ),
            nullable=False,
        ),
        sa.Column("score", sa.Double(), nullable=True),
        sa.Column("reason_code", sa.String(length=100), nullable=True),
        sa.Column("evidence", postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(
            ["attempt_id"],
            ["attempts.id"],
            name=op.f("fk_scores_attempt_id_attempts"),
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_scores")),
        sa.UniqueConstraint(
            "attempt_id",
            "evaluator",
            "evaluator_version",
            "dimension",
            name="uq_scores_dimension",
        ),
    )
    op.create_index(
        op.f("ix_scores_reason_code"), "scores", ["reason_code"], unique=False
    )
    op.create_index(op.f("ix_scores_status"), "scores", ["status"], unique=False)
    op.create_table(
        "tool_calls",
        sa.Column("id", sa.BigInteger(), sa.Identity(always=True), nullable=False),
        sa.Column("attempt_id", sa.Uuid(), nullable=False),
        sa.Column("sequence", sa.Integer(), nullable=False),
        sa.Column("call_id", sa.String(length=100), nullable=False),
        sa.Column("tool_name", sa.String(length=100), nullable=False),
        sa.Column(
            "status",
            sa.Enum(
                "ok",
                "error",
                "denied",
                "rejected",
                name="toolcallstatus",
                native_enum=False,
                length=32,
            ),
            nullable=False,
        ),
        sa.Column("schema_valid", sa.Boolean(), nullable=False),
        sa.Column("arguments", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column("raw_arguments", sa.Text(), nullable=True),
        sa.Column("output", postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column("effects", postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column("started_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("duration_ms", sa.Double(), nullable=False),
        sa.ForeignKeyConstraint(
            ["attempt_id"],
            ["attempts.id"],
            name=op.f("fk_tool_calls_attempt_id_attempts"),
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_tool_calls")),
        sa.UniqueConstraint("attempt_id", "sequence", name="uq_tool_calls_sequence"),
    )
    op.create_index(
        op.f("ix_tool_calls_status"), "tool_calls", ["status"], unique=False
    )
    op.create_index(
        op.f("ix_tool_calls_tool_name"), "tool_calls", ["tool_name"], unique=False
    )
    op.create_table(
        "trace_events",
        sa.Column("id", sa.BigInteger(), sa.Identity(always=True), nullable=False),
        sa.Column("attempt_id", sa.Uuid(), nullable=False),
        sa.Column("sequence", sa.Integer(), nullable=False),
        sa.Column(
            "event_type",
            sa.Enum(
                "attempt_started",
                "tool_requested",
                "tool_finished",
                "tool_rejected",
                "agent_finished",
                "evaluator_finished",
                "attempt_finished",
                name="eventtype",
                native_enum=False,
                length=32,
            ),
            nullable=False,
        ),
        sa.Column("status", sa.String(length=32), nullable=True),
        sa.Column("occurred_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("duration_ms", sa.Double(), nullable=True),
        sa.Column("payload", postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.ForeignKeyConstraint(
            ["attempt_id"],
            ["attempts.id"],
            name=op.f("fk_trace_events_attempt_id_attempts"),
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_trace_events")),
        sa.UniqueConstraint("attempt_id", "sequence", name="uq_trace_events_sequence"),
    )
    op.create_index(
        op.f("ix_trace_events_event_type"), "trace_events", ["event_type"], unique=False
    )


def downgrade() -> None:
    op.drop_index(op.f("ix_trace_events_event_type"), table_name="trace_events")
    op.drop_table("trace_events")
    op.drop_index(op.f("ix_tool_calls_tool_name"), table_name="tool_calls")
    op.drop_index(op.f("ix_tool_calls_status"), table_name="tool_calls")
    op.drop_table("tool_calls")
    op.drop_index(op.f("ix_scores_status"), table_name="scores")
    op.drop_index(op.f("ix_scores_reason_code"), table_name="scores")
    op.drop_table("scores")
    op.drop_index(op.f("ix_attempts_run_id"), table_name="attempts")
    op.drop_index(op.f("ix_attempts_execution_status"), table_name="attempts")
    op.drop_index(op.f("ix_attempts_evaluation_status"), table_name="attempts")
    op.drop_table("attempts")
    op.drop_index(op.f("ix_runs_task_version_id"), table_name="runs")
    op.drop_index(op.f("ix_runs_experiment_id"), table_name="runs")
    op.drop_index(op.f("ix_runs_agent_config_id"), table_name="runs")
    op.drop_table("runs")
    op.drop_index(
        op.f("ix_task_versions_dataset_version_id"), table_name="task_versions"
    )
    op.drop_index(op.f("ix_task_versions_category"), table_name="task_versions")
    op.drop_table("task_versions")
    op.drop_index(op.f("ix_experiments_status"), table_name="experiments")
    op.drop_index(op.f("ix_experiments_dataset_version_id"), table_name="experiments")
    op.drop_table("experiments")
    op.drop_index(op.f("ix_dataset_versions_dataset_id"), table_name="dataset_versions")
    op.drop_table("dataset_versions")
    op.drop_table("datasets")
    op.drop_table("agent_configs")
