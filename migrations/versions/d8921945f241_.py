"""empty message

Revision ID: d8921945f241
Revises: 5aa132f978ec
Create Date: 2020-12-20 13:04:33.808749

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'd8921945f241'
down_revision = '5aa132f978ec'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('users', sa.Column('icon_colours', sa.String(),
                                     nullable=True))
    op.add_column('users', sa.Column('selected_character',
                                     sa.String(length=6), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('users', 'selected_character')
    op.drop_column('users', 'icon_colours')
    # ### end Alembic commands ###
