"""empty message

Revision ID: 2cd3e0bd28db
Revises: 8e2b04523898
Create Date: 2020-06-21 18:43:54.300015

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "2cd3e0bd28db"
down_revision = "8e2b04523898"
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column("posts", sa.Column("open_report", sa.Boolean(), nullable=True))
    op.execute("UPDATE posts SET open_report = false;")
    op.alter_column("posts", "open_report", nullable=False)
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column("posts", "open_report")
    # ### end Alembic commands ###
