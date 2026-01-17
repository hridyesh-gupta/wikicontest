"""Add trusted_member_request_reason field to users table

Revision ID: de4074ff4ff8
Revises: 90aa0fb7e9ad
Create Date: 2026-01-16 20:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'de4074ff4ff8'
down_revision = '90aa0fb7e9ad'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Add trusted_member_request_reason column to users table
    # This field stores the reason provided by users when requesting trusted member status
    # It is required when user has less than 300 edits
    # Superadmins can view this reason when reviewing requests
    # Check if column exists before adding to handle partial migration scenarios
    conn = op.get_bind()
    inspector = sa.inspect(conn)
    columns = [col['name'] for col in inspector.get_columns('users')]
    
    if 'trusted_member_request_reason' not in columns:
        op.add_column('users', sa.Column('trusted_member_request_reason', sa.Text(), nullable=True))


def downgrade() -> None:
    # Remove trusted_member_request_reason column from users table
    conn = op.get_bind()
    inspector = sa.inspect(conn)
    columns = [col['name'] for col in inspector.get_columns('users')]
    
    if 'trusted_member_request_reason' in columns:
        op.drop_column('users', 'trusted_member_request_reason')
