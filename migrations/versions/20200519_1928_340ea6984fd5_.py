"""empty message

Revision ID: 340ea6984fd5
Revises: 9114f1efc30c
Create Date: 2020-05-19 19:28:08.192229

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '340ea6984fd5'
down_revision = '9114f1efc30c'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('messages', sa.Column('date', sa.DateTime(), nullable=True))
    op.add_column('posts', sa.Column('date', sa.DateTime(), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('posts', 'date')
    op.drop_column('messages', 'date')
    # ### end Alembic commands ###