"""Warehouse extension — add duckdb_table/profile_json/file_path to datasets.

Revision ID: 003
Revises: 002
Create Date: 2026-09-03
"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "003"
down_revision: Union[str, None] = "002"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    with op.batch_alter_table("datasets") as b:
        b.add_column(sa.Column("duckdb_table", sa.String(128), nullable=True))
        b.add_column(sa.Column("file_path", sa.String(256), nullable=True))
        b.add_column(sa.Column("profile_json", sa.Text(), nullable=True))


def downgrade() -> None:
    with op.batch_alter_table("datasets") as b:
        b.drop_column("profile_json")
        b.drop_column("file_path")
        b.drop_column("duckdb_table")
