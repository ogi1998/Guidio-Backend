"""added email verification fields

Revision ID: db9dc78a169f
Revises: 7e377dd0480c
Create Date: 2023-10-24 08:59:42.493662

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'db9dc78a169f'
down_revision = '7e377dd0480c'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column('user', sa.Column('is_verified', sa.Boolean(), nullable=True))
    op.add_column('user', sa.Column('verified_on', sa.DateTime(timezone=True), nullable=True))
    op.add_column('user', sa.Column('email_verification_token', sa.String(), nullable=True))
    op.add_column('user', sa.Column('token_expiration', sa.DateTime(timezone=True), nullable=True))

    op.execute('UPDATE "user" SET is_verified=true;')


def downgrade() -> None:
    op.drop_column('user', 'token_expiration')
    op.drop_column('user', 'email_verification_token')
    op.drop_column('user', 'verified_on')
    op.drop_column('user', 'is_verified')
