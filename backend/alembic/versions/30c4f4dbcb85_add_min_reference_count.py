"""add_min_reference_count

Revision ID: 30c4f4dbcb85
Revises: 7b8c9d0e1f2a
Create Date: 2026-01-08 12:08:04.302220

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '30c4f4dbcb85'
down_revision = '7b8c9d0e1f2a'
branch_labels = None
depends_on = None


def upgrade():
    """
    Add min_reference_count column to contests table.
    
    Default value is 0 (no requirement) for backward compatibility.
    """
    op.add_column(
        'contests',
        sa.Column(
            'min_reference_count',
            sa.Integer(),
            nullable=False,
            server_default='0',
            comment='Minimum number of references required for article submissions'
        )
    )


def downgrade():
    """
    Remove min_reference_count column.
    """
    op.drop_column('contests', 'min_reference_count')
