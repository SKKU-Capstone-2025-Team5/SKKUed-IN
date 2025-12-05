"""add contest table

Revision ID: 1234567890af
Revises: 1234567890ad
Create Date: 2025-10-30 10:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '1234567890af'
down_revision = '1234567890ad'
branch_labels = None
depends_on = None


def upgrade():
    op.create_table('contests',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('ex_name', sa.String(), nullable=False),
    sa.Column('ex_link', sa.String(), nullable=False),
    sa.Column('ex_host', sa.String(), nullable=True),
    sa.Column('ex_image', sa.String(), nullable=True),
    sa.Column('ex_start', sa.Date(), nullable=True),
    sa.Column('ex_end', sa.Date(), nullable=True),
    sa.Column('ex_flag', sa.Integer(), nullable=True),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('ex_link')
    )
    op.create_index(op.f('ix_contests_id'), 'contests', ['id'], unique=False)


def downgrade():
    op.drop_index(op.f('ix_contests_id'), table_name='contests')
    op.drop_table('contests')
