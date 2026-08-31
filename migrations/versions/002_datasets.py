"""Add datasets table (fix drift: 001 only created users).

Revision ID: 002
Revises: 001
Create Date: 2026-08-29
"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "002"
down_revision: Union[str, None] = "001"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Create datasets table if not exists (fix drift from src/core/database.py:45)
    op.create_table(
        "datasets",
        sa.Column("id", sa.Integer(), primary_key=True, index=True),
        sa.Column("username", sa.String(50), index=True, nullable=False),
        sa.Column("dataset_name", sa.String(128), nullable=False),
        sa.Column("rows", sa.Integer(), nullable=True),
        sa.Column("cols", sa.Integer(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=True),
    )
    # Optional index for (username, dataset_name) uniqueness check
    op.create_index("ix_datasets_username_name", "datasets", ["username", "dataset_name"])


def downgrade() -> None:
    op.drop_index("ix_datasets_username_name", table_name="datasets")
    op.drop_table("datasets")
