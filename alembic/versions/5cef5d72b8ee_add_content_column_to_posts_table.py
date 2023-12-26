"""add content column to posts table

Revision ID: 5cef5d72b8ee
Revises: f4995d96295a
Create Date: 2023-12-26 18:45:37.355445

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '5cef5d72b8ee'
down_revision: Union[str, None] = 'f4995d96295a'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column('posts', sa.Column('content', sa.String(), nullable=False))


def downgrade() -> None:
    op.drop_column('posts', 'content')
