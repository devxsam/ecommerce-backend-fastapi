"""Rename password to password_hash in User model

Revision ID: 1e7b6061645c
Revises: ccadd6b69276
Create Date: 2025-10-13 16:56:43.981878

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '1e7b6061645c'
down_revision: Union[str, Sequence[str], None] = 'ccadd6b69276'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass
    #op.alter_column('users', 'password', new_column_name='password_hash')


def downgrade() -> None:
    """Downgrade schema."""
    pass
