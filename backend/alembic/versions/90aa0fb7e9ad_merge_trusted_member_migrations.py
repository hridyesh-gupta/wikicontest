"""merge trusted member migrations

Revision ID: 90aa0fb7e9ad
Revises: 74585af9596b, 87b208812990
Create Date: 2026-01-16 19:30:37.900560

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '90aa0fb7e9ad'
down_revision = ('74585af9596b', '87b208812990')
branch_labels = None
depends_on = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass

