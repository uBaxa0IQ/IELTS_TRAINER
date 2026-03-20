"""initial

Revision ID: 67a38e8504ab
Revises:
Create Date: 2026-03-20 18:57:13.494757

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "67a38e8504ab"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

# Matches app.models PromptSource / SubmissionStatus (str Enum values).
_promptsource = sa.Enum("preset", "generated", "manual", name="promptsource")
_submissionstatus = sa.Enum("pending", "scored", "failed", name="submissionstatus")

_ts_default = sa.text("now()")


def upgrade() -> None:
    op.create_table(
        "users",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("email", sa.String(length=255), nullable=False),
        sa.Column("password_hash", sa.String(length=255), nullable=True),
        sa.Column("nickname", sa.String(length=32), nullable=True),
        sa.Column("google_sub", sa.String(length=128), nullable=True),
        sa.Column(
            "analysis_language",
            sa.String(length=16),
            server_default="en",
            nullable=False,
        ),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=_ts_default,
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=_ts_default,
            nullable=False,
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_users_email"), "users", ["email"], unique=True)
    op.create_index(op.f("ix_users_google_sub"), "users", ["google_sub"], unique=True)
    op.create_index(op.f("ix_users_nickname"), "users", ["nickname"], unique=False)

    op.create_table(
        "analytics_events",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("user_id", sa.String(length=36), nullable=False),
        sa.Column("event_type", sa.String(length=64), nullable=False),
        sa.Column("meta", sa.JSON(), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=_ts_default,
            nullable=False,
        ),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        op.f("ix_analytics_events_event_type"),
        "analytics_events",
        ["event_type"],
        unique=False,
    )
    op.create_index(
        op.f("ix_analytics_events_id"), "analytics_events", ["id"], unique=False
    )
    op.create_index(
        op.f("ix_analytics_events_user_id"),
        "analytics_events",
        ["user_id"],
        unique=False,
    )

    op.create_table(
        "essay_prompts",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("topic_text", sa.Text(), nullable=False),
        sa.Column("source", _promptsource, nullable=False),
        sa.Column("tags", sa.String(length=255), nullable=True),
        sa.Column("created_by_user_id", sa.String(length=36), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=_ts_default,
            nullable=False,
        ),
        sa.ForeignKeyConstraint(["created_by_user_id"], ["users.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        op.f("ix_essay_prompts_source"), "essay_prompts", ["source"], unique=False
    )

    op.create_table(
        "essay_submissions",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("user_id", sa.String(length=36), nullable=False),
        sa.Column("prompt_id", sa.String(length=36), nullable=False),
        sa.Column("essay_text", sa.Text(), nullable=False),
        sa.Column("word_count", sa.Integer(), nullable=False),
        sa.Column("timer_enabled", sa.Boolean(), nullable=False),
        sa.Column("timer_duration_seconds", sa.Integer(), nullable=True),
        sa.Column("timer_expired", sa.Boolean(), nullable=False),
        sa.Column("task_response_band", sa.Float(), nullable=True),
        sa.Column("coherence_band", sa.Float(), nullable=True),
        sa.Column("lexical_band", sa.Float(), nullable=True),
        sa.Column("grammar_band", sa.Float(), nullable=True),
        sa.Column("overall_band", sa.Float(), nullable=True),
        sa.Column("short_feedback", sa.Text(), nullable=True),
        sa.Column("analysis_json", sa.JSON(), nullable=True),
        sa.Column("status", _submissionstatus, nullable=False),
        sa.Column("failure_reason", sa.Text(), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=_ts_default,
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=_ts_default,
            nullable=False,
        ),
        sa.ForeignKeyConstraint(["prompt_id"], ["essay_prompts.id"]),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        op.f("ix_essay_submissions_prompt_id"),
        "essay_submissions",
        ["prompt_id"],
        unique=False,
    )
    op.create_index(
        op.f("ix_essay_submissions_user_id"),
        "essay_submissions",
        ["user_id"],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index(op.f("ix_essay_submissions_user_id"), table_name="essay_submissions")
    op.drop_index(op.f("ix_essay_submissions_prompt_id"), table_name="essay_submissions")
    op.drop_table("essay_submissions")

    op.drop_index(op.f("ix_essay_prompts_source"), table_name="essay_prompts")
    op.drop_table("essay_prompts")

    op.drop_index(op.f("ix_analytics_events_user_id"), table_name="analytics_events")
    op.drop_index(op.f("ix_analytics_events_id"), table_name="analytics_events")
    op.drop_index(op.f("ix_analytics_events_event_type"), table_name="analytics_events")
    op.drop_table("analytics_events")

    op.drop_index(op.f("ix_users_nickname"), table_name="users")
    op.drop_index(op.f("ix_users_google_sub"), table_name="users")
    op.drop_index(op.f("ix_users_email"), table_name="users")
    op.drop_table("users")

    bind = op.get_bind()
    _submissionstatus.drop(bind, checkfirst=True)
    _promptsource.drop(bind, checkfirst=True)
