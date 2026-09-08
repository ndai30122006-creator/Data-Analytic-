"""Versioning dataset/pipeline/dashboard (muc 15).

Revision ID: 008
Revises: 007
Create Date: 2026-09-08
"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "008"
down_revision: Union[str, None] = "007"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    for table in ("datasets", "pipelines", "dashboards"):
        op.add_column(table, sa.Column("version", sa.Integer(), nullable=True))
        op.execute(f"UPDATE {table} SET version = 1 WHERE version IS NULL")


def downgrade() -> None:
    for table in ("datasets", "pipelines", "dashboards"):
        op.drop_column(table, "version")
