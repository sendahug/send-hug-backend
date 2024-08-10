"""empty message

Revision ID: 8c92b636cfca
Revises: 01fd6b9a8c9a
Create Date: 2020-06-20 23:04:26.324746

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = "8c92b636cfca"
down_revision = "01fd6b9a8c9a"
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column("reports", sa.Column("date", sa.DateTime(), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column("reports", "date")
    # ### end Alembic commands ###
