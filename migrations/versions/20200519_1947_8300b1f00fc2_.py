"""empty message

Revision ID: 8300b1f00fc2
Revises: 340ea6984fd5
Create Date: 2020-05-19 19:47:51.083047

"""

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = "8300b1f00fc2"
down_revision = "340ea6984fd5"
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column("posts", sa.Column("given_hugs", sa.Integer(), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column("posts", "given_hugs")
    # ### end Alembic commands ###
