"""empty message

Revision ID: ee014068582b
Revises: 2a32dd21c76e
Create Date: 2020-06-14 13:00:51.679405

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'ee014068582b'
down_revision = '2a32dd21c76e'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    threads = op.create_table('threads',
                              sa.Column('id', sa.Integer(), nullable=False),
                              sa.Column('user_1_id', sa.Integer(),
                                        nullable=False),
                              sa.Column('user_2_id', sa.Integer(),
                                        nullable=False),
                              sa.ForeignKeyConstraint(['user_1_id'],
                                                      ['users.id'], ),
                              sa.ForeignKeyConstraint(['user_2_id'],
                                                      ['users.id'], ),
                              sa.PrimaryKeyConstraint('id')
                              )
    op.add_column('messages', sa.Column('thread', sa.Integer(), nullable=True))
    op.execute('UPDATE messages SET thread = 1 WHERE id = 1;')
    op.execute('UPDATE messages SET thread = 2 WHERE id = 3 OR id = 7;')
    op.execute('UPDATE messages SET thread = 3 WHERE id = 4 OR id = 9;')
    op.execute('UPDATE messages SET thread = 4 WHERE id = 5 OR id = 8;')
    op.bulk_insert(threads, [
        {'id': 1, 'user_1_id': 1, 'user_2_id': 1},
        {'id': 2, 'user_1_id': 1, 'user_2_id': 5},
        {'id': 3, 'user_1_id': 1, 'user_2_id': 4},
        {'id': 4, 'user_1_id': 4, 'user_2_id': 5}
    ])
    op.create_foreign_key(None, 'messages', 'threads', ['thread'], ['id'])
    op.alter_column('messages', 'thread', nullable=False)
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint(None, 'messages', type_='foreignkey')
    op.drop_column('messages', 'thread')
    op.drop_table('threads')
    # ### end Alembic commands ###
