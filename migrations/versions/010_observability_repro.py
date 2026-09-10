"""Observability + reproducibility (plan 2/3).

Revision ID: 010
Revises: 009
Create Date: 2026-09-10
"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "010"
down_revision: Union[str, None] = "009"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column("pipelines", sa.Column("proposal_id", sa.String(16), nullable=True))
    op.add_column("ai_proposals", sa.Column("spec_hash", sa.String(64), nullable=True))
    op.add_column("pipeline_runs", sa.Column("spec_hash", sa.String(64), nullable=True))
    op.add_column("pipeline_runs", sa.Column("engine", sa.String(16), nullable=True))
    op.add_column("pipeline_runs", sa.Column("started_at", sa.DateTime(), nullable=True))
    op.add_column("pipeline_runs", sa.Column("finished_at", sa.DateTime(), nullable=True))
    op.add_column("pipeline_runs", sa.Column("rows_out", sa.Integer(), nullable=True))


def downgrade() -> None:
    for table, col in [
        ("pipelines", "proposal_id"),
        ("ai_proposals", "spec_hash"),
        ("pipeline_runs", "spec_hash"),
        ("pipeline_runs", "engine"),
        ("pipeline_runs", "started_at"),
        ("pipeline_runs", "finished_at"),
        ("pipeline_runs", "rows_out"),
    ]:
        op.drop_column(table, col)
