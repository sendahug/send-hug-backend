"""empty message

Revision ID: e05f567d5754
Revises: 8300b1f00fc2
Create Date: 2020-05-20 12:24:23.865816

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "e05f567d5754"
down_revision = "8300b1f00fc2"
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column("users", sa.Column("username", sa.String(), nullable=False))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column("users", "username")
    # ### end Alembic commands ###
