"""add_categories_to_contests

Revision ID: 1fa03cdd51b
Revises: a1b2c3d4e5f6
Create Date: 2025-12-29 14:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

# revision identifiers, used by Alembic.
revision = '1fa03cdd51b'
down_revision = 'a1b2c3d4e5f6'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Add categories column to contests table
    # Categories will be stored as JSON array of category URLs in TEXT column
    # Check if column exists before adding to handle partial migration scenarios
    conn = op.get_bind()
    inspector = sa.inspect(conn)
    columns = [col['name'] for col in inspector.get_columns('contests')]
    
    if 'categories' not in columns:
        from sqlalchemy import text
        # MySQL doesn't allow default values for TEXT columns
        # So we add it as nullable first, then update existing rows, then make it NOT NULL
        op.add_column('contests', sa.Column('categories', sa.Text(), nullable=True))
        
        # Update any existing rows to have empty array
        conn.execute(text("UPDATE contests SET categories = '[]' WHERE categories IS NULL OR categories = ''"))
        
        # Now make it NOT NULL
        dialect_name = conn.dialect.name
        if dialect_name == 'mysql':
            conn.execute(text("ALTER TABLE contests MODIFY COLUMN categories TEXT NOT NULL"))
        else:
            op.alter_column('contests', 'categories',
                            existing_type=sa.Text(),
                            nullable=False,
                            existing_nullable=True)


def downgrade() -> None:
    # Remove categories column
    conn = op.get_bind()
    inspector = sa.inspect(conn)
    columns = [col['name'] for col in inspector.get_columns('contests')]
    
    if 'categories' in columns:
        op.drop_column('contests', 'categories')

