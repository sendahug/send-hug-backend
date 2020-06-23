"""empty message

Revision ID: 26e414955820
Revises: eb02c1ca03ec
Create Date: 2020-06-23 16:30:32.744534

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '26e414955820'
down_revision = 'eb02c1ca03ec'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('threads', sa.Column('user_1_deleted', sa.Boolean(),
                                       nullable=True))
    op.execute('UPDATE threads SET user_1_deleted = false;')
    op.alter_column('threads', 'user_1_deleted', nullable=False)
    op.add_column('threads', sa.Column('user_2_deleted', sa.Boolean(),
                                       nullable=True))
    op.execute('UPDATE threads SET user_2_deleted = false;')
    op.alter_column('threads', 'user_2_deleted', nullable=False)
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('threads', 'user_2_deleted')
    op.drop_column('threads', 'user_1_deleted')
    # ### end Alembic commands ###
