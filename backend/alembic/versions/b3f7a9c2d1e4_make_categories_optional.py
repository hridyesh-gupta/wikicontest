"""Make categories column optional (nullable)

Revision ID: b3f7a9c2d1e4
Revises: a28bebdbdc41
Create Date: 2026-03-10 16:45:00.000000

"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql


# revision identifiers, used by Alembic.
revision = "b3f7a9c2d1e4"
down_revision = "a28bebdbdc41"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Make categories column nullable (was NOT NULL with default '[]')
    op.alter_column(
        "contests",
        "categories",
        existing_type=mysql.TEXT(),
        nullable=True,
    )


def downgrade() -> None:
    # Revert categories column back to NOT NULL with default '[]'
    # First update any NULL values to '[]'
    op.execute("UPDATE contests SET categories = '[]' WHERE categories IS NULL")
    op.alter_column(
        "contests",
        "categories",
        existing_type=mysql.TEXT(),
        nullable=False,
        server_default=sa.text("'[]'"),
    )
