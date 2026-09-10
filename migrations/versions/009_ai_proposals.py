"""AI proposals — LLM proposes, human approves (muc production-grade AI).

Revision ID: 009
Revises: 008
Create Date: 2026-09-10
"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "009"
down_revision: Union[str, None] = "008"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "ai_proposals",
        sa.Column("id", sa.String(16), primary_key=True),
        sa.Column("owner", sa.String(50), nullable=False, index=True),
        sa.Column("kind", sa.String(16), nullable=False, default="pipeline"),
        sa.Column("name", sa.String(128), nullable=True),
        sa.Column("source", sa.String(128), nullable=True),
        sa.Column("target", sa.String(128), nullable=True),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("spec_json", sa.Text(), nullable=False),
        sa.Column("validations_json", sa.Text(), nullable=True),
        sa.Column("cost_json", sa.Text(), nullable=True),
        sa.Column("dry_run_json", sa.Text(), nullable=True),
        sa.Column("model_used", sa.String(64), nullable=False, default="rule-based"),
        sa.Column("status", sa.String(16), nullable=False, default="proposed"),
        sa.Column("created_at", sa.DateTime(), nullable=True),
    )


def downgrade() -> None:
    op.drop_table("ai_proposals")
