"""add submission review fields

Revision ID: ccd6aa4c2144
Revises: fc55a0c85ffc
Create Date: 2025-12-17 12:38:18.990965

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

# revision identifiers, used by Alembic.
revision = 'ccd6aa4c2144'
down_revision = 'fc55a0c85ffc'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        'submissions',
        sa.Column('reviewed_by', sa.String(length=50), nullable=True)
    )
    op.add_column(
        'submissions',
        sa.Column('reviewed_at', sa.DateTime(), nullable=True)
    )
    op.add_column(
        'submissions',
        sa.Column('review_comment', sa.Text(), nullable=True)
    )

    op.create_foreign_key(
        'fk_submissions_reviewed_by_users',
        'submissions',
        'users',
        ['reviewed_by'],
        ['username']
    )


def downgrade() -> None:
    op.drop_constraint(
        'fk_submissions_reviewed_by_users',
        'submissions',
        type_='foreignkey'
    )
    op.drop_column('submissions', 'review_comment')
    op.drop_column('submissions', 'reviewed_at')
    op.drop_column('submissions', 'reviewed_by')

