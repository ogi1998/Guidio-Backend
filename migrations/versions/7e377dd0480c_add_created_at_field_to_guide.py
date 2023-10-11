"""add_created_at_field_to_guide

Revision ID: 7e377dd0480c
Revises: 8fe5031c10e5
Create Date: 2023-10-11 11:26:27.662602

"""
import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = '7e377dd0480c'
down_revision = '8fe5031c10e5'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column('guide', sa.Column('created_at', sa.DateTime(timezone=True),
                                     server_default=sa.text('now()'), nullable=False))

    # Manually update existing rows with the current timestamp
    op.execute("UPDATE guide SET created_at = CURRENT_TIMESTAMP")


def downgrade() -> None:
    op.drop_column('guide', 'created_at')
