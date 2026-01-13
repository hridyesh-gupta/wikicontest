"""add_organizers_column

Revision ID: 7b8c9d0e1f2a
Revises: 549b0e507d5d
Create Date: 2025-01-07 14:00:00

This migration adds organizers column to contests table.
Organizers are stored as comma-separated usernames, similar to jury_members.
"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

# revision identifiers, used by Alembic.
revision = '7b8c9d0e1f2a'
down_revision = '549b0e507d5d'
branch_labels = None
depends_on = None


def upgrade():
    """
    Add organizers column to contests table.
    
    This migration:
    1. Adds organizers column (comma-separated usernames)
    2. Migrates existing creators as organizers
    3. Maintains created_by field for backward compatibility
    """
    
    # Add organizers column
    op.add_column(
        'contests',
        sa.Column(
            'organizers',
            sa.Text(),
            nullable=True,
            comment='Comma-separated list of organizer usernames'
        )
    )
    
    # Data migration: Set organizers to include creator
    # For existing contests, creator becomes the first organizer
    connection = op.get_bind()
    connection.execute(
        sa.text("""
            UPDATE contests
            SET organizers = created_by
            WHERE organizers IS NULL OR organizers = ''
        """)
    )


def downgrade():
    """
    Remove organizers column.
    
    WARNING: This will delete all organizer data except the original creator
    (which is preserved in created_by field).
    """
    op.drop_column('contests', 'organizers')