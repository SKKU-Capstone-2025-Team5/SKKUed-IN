"""Update team and user relationships

Revision ID: 1234567890b1
Revises: 1234567890af
Create Date: 2025-10-31 11:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '1234567890b1'
down_revision = '1234567890af'
branch_labels = None
depends_on = None


def upgrade():
    with op.batch_alter_table('teams', schema=None) as batch_op:
        batch_op.add_column(sa.Column('contest_id', sa.Integer(), nullable=True))
        batch_op.create_foreign_key('fk_teams_contest_id', 'contests', ['contest_id'], ['id'])


def downgrade():
    with op.batch_alter_table('teams', schema=None) as batch_op:
        batch_op.drop_constraint('fk_teams_contest_id', type_='foreignkey')
        batch_op.drop_column('contest_id')
