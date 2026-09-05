"""Pipeline steps (Plan 03).

Revision ID: 007
Revises: 006
Create Date: 2026-09-03
"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "007"
down_revision: Union[str, None] = "006"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "pipeline_steps",
        sa.Column("id", sa.Integer(), primary_key=True, index=True),
        sa.Column(
            "run_id", sa.String(16), sa.ForeignKey("pipeline_runs.id", ondelete="CASCADE"), nullable=False, index=True
        ),
        sa.Column("step_id", sa.String(32), nullable=False),
        sa.Column("status", sa.String(16), nullable=False),
        sa.Column("log", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=True),
    )


def downgrade() -> None:
    op.drop_table("pipeline_steps")
