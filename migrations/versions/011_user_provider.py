"""BYOK provider per user (provider that, het fake).

Revision ID: 011
Revises: 010
Create Date: 2026-09-10
"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "011"
down_revision: Union[str, None] = "010"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column("users", sa.Column("api_provider", sa.String(16), nullable=True))


def downgrade() -> None:
    op.drop_column("users", "api_provider")
