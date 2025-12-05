"""test revision

Revision ID: 28f198baf0c4
Revises: manual_migration_20251101
Create Date: 2025-11-06 18:17:19.465389

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '28f198baf0c4'
down_revision = 'manual_migration_20251101'
branch_labels = None
depends_on = None


def upgrade():
    with op.batch_alter_table('messages', schema=None) as batch_op:
        batch_op.add_column(sa.Column('file_url', sa.String(), nullable=True))

    with op.batch_alter_table('messages', schema=None) as batch_op:
        batch_op.add_column(sa.Column('reply_to_message_id', sa.Integer(), nullable=True))
        batch_op.create_foreign_key(
            'fk_messages_reply_to_message_id',
            'messages',
            ['reply_to_message_id'], ['id']
        )

def downgrade():
    with op.batch_alter_table('messages', schema=None) as batch_op:
        batch_op.drop_constraint('fk_messages_reply_to_message_id', type_='foreignkey')
        batch_op.drop_column('reply_to_message_id')

    with op.batch_alter_table('messages', schema=None) as batch_op:
        batch_op.drop_column('file_url')
