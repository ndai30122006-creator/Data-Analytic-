"""Pipelines + runs (Plan 03/07).

Revision ID: 006
Revises: 005
Create Date: 2026-09-03
"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "006"
down_revision: Union[str, None] = "005"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "pipelines",
        sa.Column("id", sa.String(16), primary_key=True),
        sa.Column("owner", sa.String(50), nullable=False, index=True),
        sa.Column("name", sa.String(128), nullable=False),
        sa.Column("source", sa.String(128), nullable=False),
        sa.Column("target", sa.String(128), nullable=False),
        sa.Column("spec_json", sa.Text(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=True),
    )
    op.create_table(
        "pipeline_runs",
        sa.Column("id", sa.String(16), primary_key=True),
        sa.Column(
            "pipeline_id", sa.String(16), sa.ForeignKey("pipelines.id", ondelete="CASCADE"), nullable=False, index=True
        ),
        sa.Column("status", sa.String(16), nullable=False),
        sa.Column("result_json", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=True),
    )


def downgrade() -> None:
    op.drop_table("pipeline_runs")
    op.drop_table("pipelines")
