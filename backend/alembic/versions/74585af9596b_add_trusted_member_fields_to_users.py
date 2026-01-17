"""add_trusted_member_fields_to_users

Revision ID: 74585af9596b
Revises: ed3dabd7833f
Create Date: 2026-01-16 19:07:47.441613

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '74585af9596b'
down_revision = 'ed3dabd7833f'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Add trusted member fields to users table
    # is_trusted_member: Boolean flag indicating if user can create contests
    # trusted_member_request: Boolean flag indicating if user has requested trusted member status
    # Check if columns exist before adding to handle partial migration scenarios
    conn = op.get_bind()
    inspector = sa.inspect(conn)
    columns = [col['name'] for col in inspector.get_columns('users')]
    
    if 'is_trusted_member' not in columns:
        op.add_column('users', sa.Column('is_trusted_member', sa.Boolean(), nullable=False, server_default=sa.text('0')))
    
    if 'trusted_member_request' not in columns:
        op.add_column('users', sa.Column('trusted_member_request', sa.Boolean(), nullable=False, server_default=sa.text('0')))


def downgrade() -> None:
    # Remove trusted member fields from users table
    op.drop_column('users', 'trusted_member_request')
    op.drop_column('users', 'is_trusted_member')

